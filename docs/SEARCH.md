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

## Not indexed yet

Institutional events. To add a type: add a `*_docs` CTE to the view with the
same columns, add it to `SearchEntityType`, and write a migration that
recreates the view. See also `docs/BACKLOG.md`.
