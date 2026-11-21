import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import text
from sqlmodel import Session

from server.utils.enums.search_entity_type import SearchEntityType

# pg_trgm word_similarity threshold for the `<%` operator (default 0.6 is too
# strict for typos like "calclo" -> "calculo").
TRGM_WORD_SIMILARITY_THRESHOLD = 0.45

# Arbitrary, stable key so only one worker refreshes the view at a time.
REFRESH_ADVISORY_LOCK_KEY = 7_340_211

# Shared CASE for "how current is this document": classes/subjects/professors
# of the running period first, then upcoming ones, then the rest. Documents
# without dates (buildings, classrooms) stay neutral.
_TIME_BOOST = """
    CASE
        WHEN d.starts_at IS NULL THEN 0.15
        WHEN current_date BETWEEN d.starts_at AND d.ends_at THEN 0.3
        WHEN d.starts_at > current_date THEN 0.2
        ELSE 0.0
    END
"""

_TIME_ORDER = """
    CASE
        WHEN d.starts_at IS NULL THEN 1
        WHEN current_date BETWEEN d.starts_at AND d.ends_at THEN 0
        WHEN d.starts_at > current_date THEN 1
        ELSE 2
    END
"""

_SEARCH_SQL = text(
    f"""
    WITH params AS (
        SELECT
            f_unaccent(lower(CAST(:q AS text))) AS q_norm,
            to_tsquery('pt_unaccent', CAST(:tsq AS text)) AS tsq
    ),
    scored AS (
        SELECT
            d.doc_key, d.entity_type, d.entity_id, d.title, d.subtitle,
            d.payload, d.edges,
            ts_rank_cd(d.tsv, p.tsq, 32)
            + 0.5 * word_similarity(p.q_norm, f_unaccent(lower(d.title)))
            + 0.2 * word_similarity(p.q_norm, d.search_text)
            + CASE WHEN p.q_norm = ANY(d.exact_keys) THEN 1.0 ELSE 0.0 END
            + {_TIME_BOOST}
            + 0.2 * d.prior AS score
        FROM search_document d
        CROSS JOIN params p
        WHERE (d.tsv @@ p.tsq OR p.q_norm <% d.search_text)
          AND d.entity_type = ANY(CAST(:types AS text[]))
    ),
    ranked AS (
        SELECT
            s.*,
            row_number() OVER (
                PARTITION BY s.entity_type ORDER BY s.score DESC, s.title
            ) AS rn,
            count(*) OVER (PARTITION BY s.entity_type) AS total
        FROM scored s
    )
    SELECT doc_key, entity_type, entity_id, title, subtitle, payload, edges,
           score, total
    FROM ranked
    WHERE rn <= :limit
    ORDER BY score DESC, title
    """
)

_RELATED_SQL = text(
    f"""
    SELECT doc_key, entity_type, entity_id, title, subtitle, payload, edges,
           0.0 AS score, total
    FROM (
        SELECT
            d.*,
            row_number() OVER (
                PARTITION BY d.entity_type
                ORDER BY {_TIME_ORDER}, d.ends_at DESC NULLS LAST,
                         d.prior DESC, d.title
            ) AS rn,
            count(*) OVER (PARTITION BY d.entity_type) AS total
        FROM search_document d
        WHERE (d.edges @> ARRAY[CAST(:doc_key AS text)]
               OR d.doc_key = ANY(CAST(:edges AS text[])))
          AND d.doc_key <> :doc_key
    ) x
    WHERE rn <= :limit
    ORDER BY entity_type, rn
    """
)


@dataclass
class SearchHit:
    doc_key: str
    entity_type: SearchEntityType
    entity_id: str
    title: str
    subtitle: str | None
    score: float
    total: int
    payload: dict[str, Any] = field(default_factory=dict)
    edges: list[str] = field(default_factory=list)


def normalize_query(query: str) -> str:
    """Lower-case, strip accents and collapse whitespace."""
    decomposed = unicodedata.normalize("NFKD", query.lower())
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return " ".join(stripped.split())


def build_prefix_tsquery(query: str) -> str:
    """Turn free text into a safe to_tsquery() input: AND of the tokens, with
    a prefix match on the last one so results show up while the user types.

    Only [a-z0-9] tokens survive, so the output never contains tsquery
    operators coming from the user. Returns "" when nothing is left."""
    tokens = re.findall(r"[a-z0-9]+", normalize_query(query))
    if not tokens:
        return ""
    return " & ".join([*tokens[:-1], f"{tokens[-1]}:*"])


class SearchRepository:
    @staticmethod
    def _to_hits(rows: Any) -> list[SearchHit]:
        return [
            SearchHit(
                doc_key=row.doc_key,
                entity_type=SearchEntityType(row.entity_type),
                entity_id=row.entity_id,
                title=row.title,
                subtitle=row.subtitle,
                score=float(row.score),
                total=int(row.total),
                payload=row.payload or {},
                edges=list(row.edges or []),
            )
            for row in rows
        ]

    @staticmethod
    def search(
        *,
        query: str,
        types: list[SearchEntityType],
        limit_per_type: int,
        session: Session,
    ) -> list[SearchHit]:
        """Best `limit_per_type` documents of each type for `query`, ordered by
        score. Each hit carries the total number of matches of its type."""
        tsquery = build_prefix_tsquery(query)
        if not tsquery or not types:
            return []
        connection = session.connection()
        connection.execute(
            text("SELECT set_config('pg_trgm.word_similarity_threshold', :t, true)"),
            {"t": str(TRGM_WORD_SIMILARITY_THRESHOLD)},
        )
        rows = connection.execute(
            _SEARCH_SQL,
            {
                "q": query.strip(),
                "tsq": tsquery,
                "types": [t.value for t in types],
                "limit": limit_per_type,
            },
        )
        return SearchRepository._to_hits(rows)

    @staticmethod
    def related(
        *, hit: SearchHit, limit_per_type: int, session: Session
    ) -> list[SearchHit]:
        """Documents one edge away from `hit`, in both directions: those that
        point to it (a subject's classes) and those it points to (a class's
        subject, professors, classroom and building)."""
        rows = session.connection().execute(
            _RELATED_SQL,
            {"doc_key": hit.doc_key, "edges": hit.edges, "limit": limit_per_type},
        )
        return SearchRepository._to_hits(rows)

    @staticmethod
    def get_by_doc_key(*, doc_key: str, session: Session) -> SearchHit | None:
        rows = session.connection().execute(
            text(
                "SELECT doc_key, entity_type, entity_id, title, subtitle, payload, "
                "edges, 0.0 AS score, 1 AS total "
                "FROM search_document WHERE doc_key = :doc_key"
            ),
            {"doc_key": doc_key},
        )
        hits = SearchRepository._to_hits(rows)
        return hits[0] if hits else None

    @staticmethod
    def refresh(*, session: Session) -> bool:
        """Rebuild the search index without blocking readers. Returns False
        (and does nothing) when another worker is already refreshing it."""
        connection = session.connection()
        locked = connection.execute(
            text("SELECT pg_try_advisory_xact_lock(:key)"),
            {"key": REFRESH_ADVISORY_LOCK_KEY},
        ).scalar()
        if not locked:
            return False
        connection.execute(
            text("REFRESH MATERIALIZED VIEW CONCURRENTLY search_document")
        )
        session.commit()
        return True
