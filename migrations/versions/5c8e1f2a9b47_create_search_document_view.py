"""create search_document materialized view

Revision ID: 5c8e1f2a9b47
Revises: 7a3e9c1d5b20
Create Date: 2026-11-20 12:00:00.000000

Unified, read-only index for the public general search (GET /search).
One row per public entity: subject, class, classroom, building, professor and
approved reservation (exam, event, and meeting only when it is a "monitoria").
Professors are not a table: they are "virtual" documents built from the
professors[] arrays of class and subject, keyed by a slug of the normalized
name.

Columns:
- doc_key:     unique identity, "<entity_type>:<entity_id>". entity_id alone is
               NOT unique (each table has its own id sequence).
- search_text: unaccented, lower-cased text used by pg_trgm (typos, partial names).
- tsv:         weighted full-text vector (A: code/name, B: professors/building,
               C: rooms/observation) in the pt_unaccent config.
- exact_keys:  normalized codes/names that get an exact-match boost.
- edges:       doc_keys this document links to (class -> subject, professor,
               classroom, building; ...). Adjacency list of the entity graph,
               used to expand the top result into related documents.
- prior:       static importance in [0, 1], log-normalized degree per type.

Reservations: one document per reservation (doc_key "reservation:<id>"), typed
by its child (exam/event/meeting). Only APPROVED ones. Meetings are private by
default; only those whose title mentions "monitoria" are indexed, since
monitorias are booked both as events and as meetings today. A reservation links
to its classroom/building, to the exam's subject and classes, and to any
subject whose code appears in the title ("Monitoria PEA3306").

It is refreshed periodically (server/services/cron/scheduler.py) with
REFRESH MATERIALIZED VIEW CONCURRENTLY, which needs the unique index on doc_key.

"""

from collections.abc import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "5c8e1f2a9b47"
down_revision: str | None = "7a3e9c1d5b20"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


SEARCH_DOCUMENT_VIEW = """
CREATE MATERIALIZED VIEW search_document AS
WITH
class_rooms AS (
    SELECT
        s.class_id,
        array_agg(DISTINCT 'classroom:' || cr.id) FILTER (WHERE cr.id IS NOT NULL)
            AS classroom_keys,
        array_agg(DISTINCT 'building:' || cr.building_id) FILTER (WHERE cr.id IS NOT NULL)
            AS building_keys,
        string_agg(DISTINCT cr.name, ' ') AS classroom_names,
        string_agg(DISTINCT b.name, ' ') AS building_names,
        jsonb_agg(DISTINCT jsonb_build_object(
            -- Same 0 (Monday) .. 6 (Sunday) value the rest of the API returns.
            'week_day', array_position(
                ARRAY['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY',
                      'FRIDAY', 'SATURDAY', 'SUNDAY'],
                s.week_day::text
            ) - 1,
            'start_time', to_char(s.start_time, 'HH24:MI'),
            'end_time', to_char(s.end_time, 'HH24:MI'),
            'classroom', cr.name,
            'building', b.name
        )) AS schedules
    FROM schedule s
    LEFT JOIN classroom cr ON cr.id = s.classroom_id
    LEFT JOIN building b ON b.id = cr.building_id
    WHERE s.class_id IS NOT NULL
    GROUP BY s.class_id
),
class_docs AS (
    SELECT
        'class:' || c.id AS doc_key,
        'class'::text AS entity_type,
        c.id::text AS entity_id,
        sub.code || ' · Turma ' || c.code AS title,
        sub.name AS subtitle,
        f_unaccent(lower(concat_ws(' ',
            sub.code, sub.name, 'turma ' || c.code,
            array_to_string(c.professors, ' '),
            cr.classroom_names, cr.building_names
        ))) AS search_text,
        setweight(to_tsvector('pt_unaccent', sub.code || ' ' || sub.name), 'A')
        || setweight(to_tsvector('pt_unaccent', array_to_string(c.professors, ' ')), 'B')
        || setweight(to_tsvector('pt_unaccent',
            concat_ws(' ', cr.classroom_names, cr.building_names)), 'C') AS tsv,
        ARRAY[f_unaccent(lower(sub.code))] AS exact_keys,
        ARRAY['subject:' || sub.id]
        || COALESCE((
            SELECT array_agg(DISTINCT 'professor:' || professor_slug(p))
            FROM unnest(c.professors) AS p
            WHERE professor_slug(p) <> ''
        ), ARRAY[]::text[])
        || COALESCE(cr.classroom_keys, ARRAY[]::text[])
        || COALESCE(cr.building_keys, ARRAY[]::text[]) AS edges,
        c.start_date AS starts_at,
        c.end_date AS ends_at,
        0::double precision AS degree,
        jsonb_build_object(
            'code', c.code,
            'subject_id', sub.id,
            'subject_code', sub.code,
            'subject_name', sub.name,
            'professors', to_jsonb(c.professors),
            'start_date', c.start_date,
            'end_date', c.end_date,
            'schedules', COALESCE(cr.schedules, '[]'::jsonb)
        ) AS payload
    FROM "class" c
    JOIN subject sub ON sub.id = c.subject_id
    LEFT JOIN class_rooms cr ON cr.class_id = c.id
    WHERE trim(sub.code) <> ''
),
subject_stats AS (
    SELECT
        subject_id,
        count(*) AS class_count,
        min(start_date) AS starts_at,
        max(end_date) AS ends_at
    FROM "class"
    GROUP BY subject_id
),
subject_docs AS (
    SELECT
        'subject:' || sub.id AS doc_key,
        'subject'::text AS entity_type,
        sub.id::text AS entity_id,
        sub.code || ' - ' || sub.name AS title,
        (
            SELECT string_agg(trim(p), ', ')
            FROM unnest(sub.professors) AS p
            WHERE trim(p) <> ''
        ) AS subtitle,
        f_unaccent(lower(concat_ws(' ',
            sub.code, sub.name, array_to_string(sub.professors, ' ')
        ))) AS search_text,
        setweight(to_tsvector('pt_unaccent', sub.code || ' ' || sub.name), 'A')
        || setweight(to_tsvector('pt_unaccent',
            array_to_string(sub.professors, ' ')), 'B') AS tsv,
        ARRAY[f_unaccent(lower(sub.code)), f_unaccent(lower(sub.name))] AS exact_keys,
        COALESCE((
            SELECT array_agg(DISTINCT 'professor:' || professor_slug(p))
            FROM unnest(sub.professors) AS p
            WHERE professor_slug(p) <> ''
        ), ARRAY[]::text[]) AS edges,
        st.starts_at,
        st.ends_at,
        COALESCE(st.class_count, 0)::double precision AS degree,
        jsonb_build_object(
            'code', sub.code,
            'name', sub.name,
            'professors', to_jsonb(sub.professors),
            'class_count', COALESCE(st.class_count, 0)
        ) AS payload
    FROM subject sub
    LEFT JOIN subject_stats st ON st.subject_id = sub.id
    WHERE trim(sub.code) <> ''
),
classroom_stats AS (
    SELECT classroom_id, count(*) AS schedule_count
    FROM schedule
    WHERE classroom_id IS NOT NULL
    GROUP BY classroom_id
),
classroom_docs AS (
    SELECT
        'classroom:' || cr.id AS doc_key,
        'classroom'::text AS entity_type,
        cr.id::text AS entity_id,
        cr.name AS title,
        b.name AS subtitle,
        f_unaccent(lower(concat_ws(' ', cr.name, b.name, cr.observation))) AS search_text,
        setweight(to_tsvector('pt_unaccent', cr.name), 'A')
        || setweight(to_tsvector('pt_unaccent', COALESCE(b.name, '')), 'B')
        || setweight(to_tsvector('pt_unaccent', COALESCE(cr.observation, '')), 'C') AS tsv,
        ARRAY[f_unaccent(lower(cr.name))] AS exact_keys,
        ARRAY['building:' || cr.building_id] AS edges,
        NULL::date AS starts_at,
        NULL::date AS ends_at,
        COALESCE(cs.schedule_count, 0)::double precision AS degree,
        jsonb_build_object(
            'name', cr.name,
            'building_id', cr.building_id,
            'building', b.name,
            'floor', cr.floor,
            'capacity', cr.capacity,
            'accessibility', cr.accessibility,
            'air_conditioning', cr.air_conditioning
        ) AS payload
    FROM classroom cr
    JOIN building b ON b.id = cr.building_id
    LEFT JOIN classroom_stats cs ON cs.classroom_id = cr.id
),
building_docs AS (
    SELECT
        'building:' || b.id AS doc_key,
        'building'::text AS entity_type,
        b.id::text AS entity_id,
        b.name AS title,
        NULL::text AS subtitle,
        f_unaccent(lower(b.name)) AS search_text,
        setweight(to_tsvector('pt_unaccent', b.name), 'A') AS tsv,
        ARRAY[f_unaccent(lower(b.name))] AS exact_keys,
        ARRAY[]::text[] AS edges,
        NULL::date AS starts_at,
        NULL::date AS ends_at,
        (SELECT count(*) FROM classroom cr WHERE cr.building_id = b.id)::double precision
            AS degree,
        jsonb_build_object(
            'name', b.name,
            'classroom_count',
            (SELECT count(*) FROM classroom cr WHERE cr.building_id = b.id)
        ) AS payload
    FROM building b
),
professor_raw AS (
    SELECT
        professor_slug(p) AS slug,
        clean_professor_name(p) AS name,
        c.id AS class_id,
        c.subject_id,
        c.start_date,
        c.end_date
    FROM "class" c
    CROSS JOIN LATERAL unnest(c.professors) AS p
    UNION ALL
    SELECT
        professor_slug(p),
        clean_professor_name(p),
        NULL::integer,
        sub.id,
        NULL::date,
        NULL::date
    FROM subject sub
    CROSS JOIN LATERAL unnest(sub.professors) AS p
    WHERE trim(sub.code) <> ''
),
professor_docs AS (
    SELECT
        'professor:' || pr.slug AS doc_key,
        'professor'::text AS entity_type,
        pr.slug AS entity_id,
        mode() WITHIN GROUP (ORDER BY pr.name) AS title,
        NULL::text AS subtitle,
        f_unaccent(lower(string_agg(DISTINCT pr.name, ' '))) AS search_text,
        setweight(to_tsvector('pt_unaccent', string_agg(DISTINCT pr.name, ' ')), 'A') AS tsv,
        array_agg(DISTINCT f_unaccent(lower(pr.name))) AS exact_keys,
        COALESCE(
            array_agg(DISTINCT 'subject:' || pr.subject_id)
                FILTER (WHERE pr.subject_id IS NOT NULL),
            ARRAY[]::text[]
        ) AS edges,
        min(pr.start_date) AS starts_at,
        max(pr.end_date) AS ends_at,
        count(DISTINCT pr.class_id)::double precision AS degree,
        jsonb_build_object(
            'name', mode() WITHIN GROUP (ORDER BY pr.name),
            'class_count', count(DISTINCT pr.class_id),
            'subject_count', count(DISTINCT pr.subject_id)
        ) AS payload
    FROM professor_raw pr
    WHERE pr.slug <> ''
    GROUP BY pr.slug
),
reservation_base AS (
    SELECT
        r.id,
        r.title,
        r.type::text AS rtype,
        s.id AS schedule_id,
        s.start_date,
        s.end_date,
        s.start_time,
        s.end_time,
        s.week_day::text AS week_day,
        s.recurrence::text AS recurrence,
        cr.id AS classroom_id,
        cr.name AS classroom,
        b.id AS building_id,
        b.name AS building,
        ev.type::text AS event_type,
        ev.link AS event_link,
        ex.id AS exam_id,
        ex.subject_id AS exam_subject_id
    FROM reservation r
    LEFT JOIN schedule s ON s.reservation_id = r.id
    LEFT JOIN classroom cr ON cr.id = s.classroom_id
    LEFT JOIN building b ON b.id = cr.building_id
    LEFT JOIN event ev ON ev.reservation_id = r.id
    LEFT JOIN exam ex ON ex.reservation_id = r.id
    WHERE r.status = 'APPROVED'
      AND (
          r.type IN ('EXAM', 'EVENT')
          OR (r.type = 'MEETING' AND f_unaccent(lower(r.title)) LIKE '%monitori%')
      )
),
reservation_subjects AS (
    SELECT rb.id AS reservation_id, sub.id AS subject_id, sub.code, sub.name
    FROM reservation_base rb
    JOIN subject sub ON sub.id = rb.exam_subject_id
    UNION
    -- Subject codes cited in the title: "PEA3306", "PEA 3306" or "4323101".
    SELECT rb.id, sub.id, sub.code, sub.name
    FROM reservation_base rb
    CROSS JOIN LATERAL regexp_matches(
        rb.title, '([A-Za-z]{3}) ?([0-9]{4})|([0-9]{7})', 'g'
    ) AS m
    JOIN subject sub ON sub.code = COALESCE(upper(m[1]) || m[2], m[3])
),
reservation_docs AS (
    SELECT
        'reservation:' || rb.id AS doc_key,
        lower(rb.rtype) AS entity_type,
        rb.id::text AS entity_id,
        rb.title,
        NULLIF(concat_ws(' · ', rb.classroom, rb.building), '') AS subtitle,
        f_unaccent(lower(concat_ws(' ',
            rb.title, subj.texts, rb.classroom, rb.building
        ))) AS search_text,
        setweight(to_tsvector('pt_unaccent', rb.title), 'A')
        || setweight(to_tsvector('pt_unaccent', COALESCE(subj.texts, '')), 'B')
        || setweight(to_tsvector('pt_unaccent',
            concat_ws(' ', rb.classroom, rb.building)), 'C') AS tsv,
        ARRAY[f_unaccent(lower(rb.title))] AS exact_keys,
        COALESCE(subj.keys, ARRAY[]::text[])
        || COALESCE(cls.keys, ARRAY[]::text[])
        || CASE WHEN rb.classroom_id IS NULL THEN ARRAY[]::text[]
                ELSE ARRAY['classroom:' || rb.classroom_id,
                           'building:' || rb.building_id] END AS edges,
        COALESCE(occ.first_date, rb.start_date) AS starts_at,
        COALESCE(occ.last_date, rb.end_date) AS ends_at,
        0::double precision AS degree,
        jsonb_build_object(
            'start_date', rb.start_date,
            'end_date', rb.end_date,
            'start_time', to_char(rb.start_time, 'HH24:MI'),
            'end_time', to_char(rb.end_time, 'HH24:MI'),
            -- Same 0 (Monday) .. 6 (Sunday) value the rest of the API returns.
            'week_day', array_position(
                ARRAY['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY',
                      'FRIDAY', 'SATURDAY', 'SUNDAY'],
                rb.week_day
            ) - 1,
            'recurrence', lower(rb.recurrence),
            'classroom_id', rb.classroom_id,
            'classroom', rb.classroom,
            'building_id', rb.building_id,
            'building', rb.building,
            'event_type', lower(rb.event_type),
            -- Only events expose their link; a meeting link may be private.
            'link', rb.event_link,
            'subjects', COALESCE(subj.json, '[]'::jsonb),
            'occurrences', COALESCE(occ.json, '[]'::jsonb)
        ) AS payload
    FROM reservation_base rb
    LEFT JOIN LATERAL (
        SELECT
            string_agg(rs.code || ' ' || rs.name, ' ') AS texts,
            array_agg(DISTINCT 'subject:' || rs.subject_id) AS keys,
            jsonb_agg(jsonb_build_object(
                'id', rs.subject_id, 'code', rs.code, 'name', rs.name
            )) AS json
        FROM reservation_subjects rs
        WHERE rs.reservation_id = rb.id
    ) subj ON true
    LEFT JOIN LATERAL (
        SELECT array_agg(DISTINCT 'class:' || ecl.class_id) AS keys
        FROM examclasslink ecl
        WHERE ecl.exam_id = rb.exam_id
    ) cls ON true
    LEFT JOIN LATERAL (
        SELECT
            min(o.date) AS first_date,
            max(o.date) AS last_date,
            jsonb_agg(jsonb_build_object(
                'date', o.date,
                'start_time', to_char(o.start_time, 'HH24:MI'),
                'end_time', to_char(o.end_time, 'HH24:MI')
            ) ORDER BY o.date, o.start_time) AS json
        FROM occurrence o
        WHERE o.schedule_id = rb.schedule_id
    ) occ ON true
),
all_docs AS (
    SELECT * FROM class_docs
    UNION ALL SELECT * FROM subject_docs
    UNION ALL SELECT * FROM classroom_docs
    UNION ALL SELECT * FROM building_docs
    UNION ALL SELECT * FROM professor_docs
    UNION ALL SELECT * FROM reservation_docs
)
SELECT
    doc_key,
    entity_type,
    entity_id,
    title,
    subtitle,
    search_text,
    tsv,
    exact_keys,
    edges,
    starts_at,
    ends_at,
    COALESCE(
        ln(1 + degree) / NULLIF(ln(1 + max(degree) OVER (PARTITION BY entity_type)), 0),
        0
    ) AS prior,
    payload
FROM all_docs
WITH DATA
"""


def upgrade() -> None:
    # Both are "trusted" extensions (PG >= 13): the database owner can create
    # them without superuser.
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # unaccent() is only STABLE (it depends on the search_path); this wrapper
    # pins the dictionary so it can be used anywhere an IMMUTABLE function is
    # required.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION f_unaccent(text) RETURNS text
        LANGUAGE sql IMMUTABLE PARALLEL SAFE STRICT AS
        $$ SELECT public.unaccent('public.unaccent'::regdictionary, $1) $$
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION search_slug(text) RETURNS text
        LANGUAGE sql IMMUTABLE PARALLEL SAFE STRICT AS
        $$ SELECT trim(both '-' from
               regexp_replace(f_unaccent(lower(trim($1))), '[^a-z0-9]+', '-', 'g')) $$
        """
    )
    # The crawler marks the professor in charge as "(R) Name"; without this the
    # same person becomes two professor documents.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION clean_professor_name(text) RETURNS text
        LANGUAGE sql IMMUTABLE PARALLEL SAFE STRICT AS
        $$ SELECT trim(regexp_replace(trim($1), '^\\(R\\)\\s*', '', 'i')) $$
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION professor_slug(text) RETURNS text
        LANGUAGE sql IMMUTABLE PARALLEL SAFE STRICT AS
        $$ SELECT search_slug(clean_professor_name($1)) $$
        """
    )

    # Portuguese stemming + accent folding, so "calculo" matches "Cálculo".
    op.execute("CREATE TEXT SEARCH CONFIGURATION pt_unaccent (COPY = portuguese)")
    op.execute(
        """
        ALTER TEXT SEARCH CONFIGURATION pt_unaccent
        ALTER MAPPING FOR hword, hword_part, word WITH unaccent, portuguese_stem
        """
    )

    op.execute(SEARCH_DOCUMENT_VIEW)
    op.execute(
        "CREATE UNIQUE INDEX ix_search_document_doc_key ON search_document (doc_key)"
    )
    op.execute(
        "CREATE INDEX ix_search_document_entity_type ON search_document (entity_type)"
    )
    op.execute("CREATE INDEX ix_search_document_tsv ON search_document USING gin (tsv)")
    op.execute(
        "CREATE INDEX ix_search_document_search_text_trgm "
        "ON search_document USING gin (search_text gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX ix_search_document_edges ON search_document USING gin (edges)"
    )


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS search_document")
    op.execute("DROP TEXT SEARCH CONFIGURATION IF EXISTS pt_unaccent")
    op.execute("DROP FUNCTION IF EXISTS professor_slug(text)")
    op.execute("DROP FUNCTION IF EXISTS clean_professor_name(text)")
    op.execute("DROP FUNCTION IF EXISTS search_slug(text)")
    op.execute("DROP FUNCTION IF EXISTS f_unaccent(text)")
    # The unaccent/pg_trgm extensions are left installed on purpose: they are
    # harmless and other objects may come to depend on them.
