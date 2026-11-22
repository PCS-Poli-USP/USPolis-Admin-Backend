import re
from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy import CursorResult, delete, text
from sqlmodel import Session, col

from server.models.database.search_query_log_db_model import SearchQueryLog
from server.repositories.search_repository import normalize_query
from server.utils.enums.search_entity_type import SearchEntityType

# 8+ digits, optionally split by spaces, dots, dashes or slashes: CPF, RG,
# phone and 8-digit USP numbers. Subject codes (7 digits, e.g. 0303200) and
# room names stay loggable.
_LONG_NUMBER = re.compile(r"\d(?:[\s./-]?\d){7,}")


def is_loggable_query(query: str) -> bool:
    """False for queries that look like personal data (e-mails and long
    numbers). The log is anonymous, so what people type must not identify
    them either; such searches still work, they are just not recorded."""
    return "@" not in query and _LONG_NUMBER.search(query) is None


def normalize_log_query(query: str) -> str | None:
    """The query as stored in the log, or None when it must not be stored
    (empty after normalization, or looks like personal data)."""
    normalized = normalize_query(query)[:100]
    if not normalized or not is_loggable_query(normalized):
        return None
    return normalized


def normalize_log_types(types: list[SearchEntityType] | None) -> list[str]:
    """Sorted type values; the full set and no filter mean the same and are
    both stored as [] ("all types")."""
    selected = set(types or [])
    if not selected or selected == set(SearchEntityType.values()):
        return []
    return sorted(t.value for t in selected)


@dataclass
class SearchQueryStat:
    query: str
    searches: int
    empty_searches: int
    last_result_count: int
    last_searched_at: datetime


@dataclass
class SearchQueryTotals:
    searches: int
    distinct_queries: int
    empty_searches: int


# ON CONFLICT: two requests creating the same row at once end up as one row
# with both searches counted.
_UPSERT_SQL = text(
    """
    INSERT INTO searchquerylog
        (day, query, types, searches, empty_searches, last_result_count,
         last_searched_at)
    VALUES
        (:day, :query, CAST(:types AS varchar[]), 1, :empty, :result_count, :now)
    ON CONFLICT ON CONSTRAINT uq_searchquerylog_day_query_types DO UPDATE SET
        searches = searchquerylog.searches + 1,
        empty_searches = searchquerylog.empty_searches + EXCLUDED.empty_searches,
        last_result_count = EXCLUDED.last_result_count,
        last_searched_at = EXCLUDED.last_searched_at
    """
)

_STATS_SQL = text(
    """
    SELECT
        query,
        sum(searches) AS searches,
        sum(empty_searches) AS empty_searches,
        (array_agg(last_result_count ORDER BY last_searched_at DESC))[1]
            AS last_result_count,
        max(last_searched_at) AS last_searched_at
    FROM searchquerylog
    WHERE day >= :since
    GROUP BY query
    HAVING NOT :only_empty OR sum(empty_searches) > 0
    ORDER BY
        CASE WHEN :only_empty THEN sum(empty_searches) ELSE sum(searches) END DESC,
        max(last_searched_at) DESC,
        query
    LIMIT :limit
    """
)

_TOTALS_SQL = text(
    """
    SELECT
        COALESCE(sum(searches), 0) AS searches,
        count(DISTINCT query) AS distinct_queries,
        COALESCE(sum(empty_searches), 0) AS empty_searches
    FROM searchquerylog
    WHERE day >= :since
    """
)


def _params(
    *, day: date, query: str, types: list[str], result_count: int, now: datetime
) -> dict[str, object]:
    return {
        "day": day,
        "query": query,
        "types": types,
        "result_count": result_count,
        "empty": 1 if result_count == 0 else 0,
        "now": now,
    }


class SearchQueryLogRepository:
    @staticmethod
    def exists(*, day: date, query: str, types: list[str], session: Session) -> bool:
        """Whether (day, query, types) already has a row, i.e. recording it
        again only bumps counters. A lookup on the unique key."""
        row = session.connection().execute(
            text(
                "SELECT 1 FROM searchquerylog WHERE day = :day AND query = :query "
                "AND types = CAST(:types AS varchar[])"
            ),
            {"day": day, "query": query, "types": types},
        )
        return row.first() is not None

    @staticmethod
    def create_or_increment(
        *,
        day: date,
        query: str,
        types: list[str],
        result_count: int,
        now: datetime,
        session: Session,
    ) -> None:
        """Count one search of (day, query, types), adding its row when it is
        the first one (also when a concurrent request created it meanwhile).
        Caller commits."""
        session.connection().execute(
            _UPSERT_SQL,
            _params(
                day=day, query=query, types=types, result_count=result_count, now=now
            ),
        )

    @staticmethod
    def count_rows_of_day(*, day: date, session: Session) -> int:
        """Distinct (query, types) rows of `day`: the daily cap counts these.
        An index range scan on the unique key."""
        return int(
            session.connection()
            .execute(
                text("SELECT count(*) FROM searchquerylog WHERE day = :day"),
                {"day": day},
            )
            .scalar_one()
        )

    @staticmethod
    def get_stats(
        *, since: date, only_empty: bool, limit: int, session: Session
    ) -> list[SearchQueryStat]:
        """Searches per normalized query from `since` on (all type filters
        together), most searched first. With `only_empty`, only queries that
        returned nothing at least once, ordered by how often that happened."""
        rows = session.connection().execute(
            _STATS_SQL, {"since": since, "only_empty": only_empty, "limit": limit}
        )
        return [
            SearchQueryStat(
                query=row.query,
                searches=int(row.searches),
                empty_searches=int(row.empty_searches),
                last_result_count=int(row.last_result_count),
                last_searched_at=row.last_searched_at,
            )
            for row in rows
        ]

    @staticmethod
    def get_totals(*, since: date, session: Session) -> SearchQueryTotals:
        row = session.connection().execute(_TOTALS_SQL, {"since": since}).one()
        return SearchQueryTotals(
            searches=int(row.searches),
            distinct_queries=int(row.distinct_queries),
            empty_searches=int(row.empty_searches),
        )

    @staticmethod
    def delete_older_than(*, cutoff: date, session: Session) -> int:
        """Used by the retention job: rows of days before `cutoff`. Caller
        commits."""
        result: CursorResult[tuple[()]] = session.connection().execute(
            delete(SearchQueryLog).where(col(SearchQueryLog.day) < cutoff)
        )
        return result.rowcount
