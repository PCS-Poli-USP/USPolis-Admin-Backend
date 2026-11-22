# Public general search

`GET /search?q=...` powers the "search anything" page of the frontend. It finds
subjects, classes, classrooms, buildings, professors and approved reservations
(exams, events, and meetings that are monitorias) from one free-text query,
without any AI model: only Postgres full-text search and `pg_trgm`.

The theory behind each part (stemming, inverted index, cover density ranking,
trigrams, the entity graph, PageRank) is explained, in Portuguese, in the
frontend developer docs: `USPolis-Admin-Frontend/docs/dev/search/index.md`
(published under Referência → Busca geral).

`GET /search/documents/{doc_key}` returns one document with its related ones;
the frontend uses it when a result is clicked.

## How it works

1. **Index.** The materialized view `search_document`
   (`migrations/versions/5c8e1f2a9b47_create_search_document_view.py`) holds one
   row per public entity. Professors are not a table: they come from the
   `professors[]` arrays of `class` and `subject`, keyed by a slug of the
   normalized name, with the crawler's `(R)` marker removed
   (`clean_professor_name`), so `(R) João Silva` and `João Silva` are one document.
2. **Identity.** `entity_id` is only unique within a type (each table has its
   own id sequence), so the key is `doc_key = "<entity_type>:<entity_id>"`.
3. **Matching.** A row matches when its weighted `tsvector` (config
   `pt_unaccent`: Portuguese stemming + accent folding) matches the query, or
   when `pg_trgm` word similarity is at least 0.45 (typos, partial names).
   `build_prefix_tsquery` keeps only `[a-z0-9]` tokens and adds a prefix match
   on the last one, so results show up while the user types.
4. **Ranking** (`SearchRepository.search`):

   | Term | Weight | Why |
   |---|---|---|
   | `ts_rank_cd` (normalized to 0..1) | 1.0 | lexical match, code/name (A) > professors/building (B) > rooms (C) |
   | word similarity with the title | 0.5 | the document whose *title* matches wins (a professor over the subjects that list them) |
   | word similarity with all the text | 0.2 | typos and partial matches anywhere |
   | exact code/name (`exact_keys`) | +1.0 | `MAC0110`, `B2-04`, `Biênio` go to the top |
   | time | 0 to 0.3 | current period > upcoming > undated (rooms, buildings) > past |
   | `prior` | 0.2 | log-normalized degree per type (classes of a subject, schedules of a room) |

5. **Graph expansion.** The `edges` column is the adjacency list of the entity
   graph (class → subject, professors, classroom, building; subject → professors;
   classroom → building; professor → subjects). The top result is expanded one
   edge away in both directions (`SearchRepository.related`), with a GIN index
   on `edges`. That is the "knowledge panel" of the response (`top.related`).

## Freshness

The view is rebuilt with `REFRESH MATERIALIZED VIEW CONCURRENTLY` (readers are
never blocked) every `SEARCH_INDEX_REFRESH_SECONDS` (default 600) by
`server/services/cron/search_index_task.py`. Every worker runs the timer; a
Postgres advisory lock makes the others skip while one is refreshing. Changes
take up to that interval to show up in the search.

Manual refresh: `REFRESH MATERIALIZED VIEW CONCURRENTLY search_document;`

## Reservations and privacy

- One document per reservation, `doc_key = "reservation:<id>"`, typed by its
  child row (`exam`, `event`, `meeting`). Only `APPROVED` reservations.
- Meetings are private by default. Only meetings whose title contains
  "monitoria" are indexed, because a third of the approved monitorias are
  booked as meetings today. Monitorias have no type of their own yet.
- The reservation `reason` is never indexed, and only events expose their
  `link` (a meeting link may be private).
- A reservation links to its classroom/building, to the exam's subject and
  classes (`examclasslink`), and to any subject whose code appears in the title
  (`PEA3306`, `PEA 3306`, `4323101`).
- The payload carries the real occurrence dates, so the frontend can tell
  "happening now", "today at 15:00" or "next: 24/11".

## Query log

`POST /search/log` (body `{"q": "...", "types": [...]}`, always `204`) records
a search the user settled on, so we can see what people look for and do not
find. The frontend calls it once per query, when the query stays unchanged for
2 s or when a result is opened, never on every keystroke (that would log every
prefix).

Table `searchquerylog` (model
`server/models/database/search_query_log_db_model.py`), **aggregated per day**:
one row per `(day, query, types)` (unique key), with counters.

| Column | Content |
|---|---|
| `day` | Brazil date |
| `query` | normalized query (`normalize_query`: lower case, no accents, single spaces) |
| `types` | sorted type filter; empty means all types |
| `searches` / `empty_searches` | searches that day / of those, how many returned nothing |
| `last_result_count` | matches of the latest search, **recomputed by the server**, never taken from the client |
| `last_searched_at` | time of the latest search |

### Privacy

No user, IP, user agent or session id is stored, and the per-day aggregation
drops the time of each search, so searches cannot be linked to a person or to
each other. Queries that look like personal data (an `@`, or 8+ digits
possibly split by `.`, `-`, `/` or spaces: CPF, phone, 8-digit USP numbers)
are accepted but not stored (`is_loggable_query`); 7-digit subject codes are
still logged. Rows older than `SEARCH_LOG_RETENTION_DAYS` (default 365) are
deleted by the daily task `purge_old_search_logs`.

### Flood guards

The endpoint is public and has no session (the cookie CSRF check does not
apply, and CORS only stops browsers on other sites), so anyone can write to
it. `server/services/search_log_service.py` keeps that from flooding the
database:

1. **Aggregation.** Repeating a query only bumps the counters of its row
   (`INSERT ... ON CONFLICT DO UPDATE`), so requests alone never grow the
   table; only distinct queries do, and only they spend the quotas below.
2. **Per-IP quota.** One client may add at most
   `SEARCH_LOG_MAX_NEW_QUERIES_PER_IP_PER_DAY` (default 200) new rows per day,
   counted in Redis like the rate limiter (key `sl:ip:<ip>:<day>`, 2-day TTL,
   IPv6 grouped by /64, IP from `request.client`, which Uvicorn resolves from
   `X-Forwarded-For` only for trusted proxies). The IP never reaches Postgres.
   200 leaves room for the USP NAT IPs (dozens of people behind one IP),
   since repeated queries cost nothing.
3. **Daily cap.** At most `SEARCH_LOG_MAX_NEW_QUERIES_PER_DAY` (default 5000)
   new rows per day for everyone, checked in Postgres, so it holds even
   without Redis. With the retention this bounds the table at
   5000 x 365 = 1.8M rows, about 365 MB worst case (~200 bytes per row with
   its index), however many IPs attack. One IP alone fills at most 4% of a
   day's cap.

A dropped search is still a `204` (the search already happened; only its
record is lost), and known queries of the day keep being counted. Each cap
logs a warning once per day and worker when reached. Without Redis (unset or
unreachable, or any Redis error) the per-IP quota fails open, like the rate
limiter; the daily cap still applies. The result count search only runs when
something will be written, so dropped records cost no extra search. On top of
all this, every request goes through the API-wide per-IP rate limit.

Not prevented: inflating the count of an existing query to push it up the
report. It does not grow the database, only skews the report, and is bounded
by the rate limit. The two caps are approximate under concurrency (two new
queries checked at the same time may both pass the last slot).

### Admin summary

`GET /admin/search-logs/summary?days=30&only_empty=false&limit=50` (admin)
returns the window totals (`total_searches`, `distinct_queries`,
`empty_searches`) and one row per normalized query, all type filters and days
together (`searches`, `empty_searches`, `last_result_count`,
`last_searched_at`). `days=30` means today and the 29 days before. With
`only_empty=true` it lists the queries that returned nothing at least once,
most frequent first: the gaps of the search. The frontend page is
Admin › Registro de Buscas (`/admin/search-logs`).

## Not indexed yet

Institutional events. To add a type: add a `*_docs` CTE to the view with the
same columns, add it to `SearchEntityType`, and write a migration that
recreates the view. See also `docs/BACKLOG.md`.
