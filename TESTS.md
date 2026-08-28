# TESTS.md

## 1. Overview

This document is a living reference for how the backend's automated test suite is organized, how to run it, what it currently covers, and what it doesn't. Update it whenever a new test tier or fixture/factory convention is introduced, and re-measure the "Current metrics" section (§6) whenever a significant batch of tests is added — those numbers are a snapshot, not something kept automatically in sync.

## 2. Running the tests

Prerequisites: a local PostgreSQL instance and `TEST_DATABASE_URI`/`TEST_DATABASE_NAME`/`TEST_ALEMBIC_URL` set in `.env` (see `.env.example` and the main `README.md`'s Test section for setup).

```bash
poetry install --with test
poetry run pytest
```

`pytest` now runs with coverage instrumentation baked into `pyproject.toml`'s `addopts`:
- `--cov=server` — measures coverage over the `server/` package only.
- `--cov-report=term-missing` — prints per-file missed line numbers in the terminal.
- `--cov-report=html` — writes an interactive report to `htmlcov/index.html` (gitignored).
- `branch = true` in `[tool.coverage.run]` — also tracks branch coverage, not just line coverage (see §8 for why that matters here specifically).

There is no `--cov-fail-under` gate yet — this round only established a baseline (§6); enforcing a minimum threshold is listed as future work in §8.

**Test isolation**: each test gets a fresh DB state via `tests/conftest.py`'s `session` fixture, which registers a `truncate_tables(username)` Postgres function (created once at collection time) and calls it as a finalizer after every test — every table (except `alembic_version`) is truncated with `RESTART IDENTITY CASCADE`. Migrations are applied once per test session via the autouse, session-scoped `apply_migrations` fixture. This means tests are fully isolated from each other but pay a truncation cost every test — there is no per-test transaction/rollback optimization in place today.

## 3. Test tiers and directory layout

| Directory | Purpose | DB / HTTP? | Files |
|---|---|---|---|
| `tests/api/admin` | Full HTTP tests for admin-only routes, via the `client` fixture | Yes (DB + `TestClient`) | 3 |
| `tests/api/authenticated` | HTTP tests for routes requiring any logged-in user | Yes | 2 |
| `tests/api/public` | HTTP tests for no-auth/optional-auth routes | Yes | 0 — empty scaffolding |
| `tests/api/restricted` | HTTP tests for routes requiring admin-or-group-member | Yes | 6 |
| `tests/integration/repositories` | DB-backed repository tests, no HTTP layer | Yes (DB only) | 2 |
| `tests/integration/services` | DB-backed service-layer tests | Yes | 0 — empty scaffolding |
| `tests/unit/models` | Pure-Python model-logic tests, no DB/session | No | 1 |
| `tests/unit/services` | Pure-Python service-logic tests | No | 0 — empty scaffolding |
| `tests/unit/utils` | Pure-Python utility tests | No | 0 — empty scaffolding |
| `tests/e2e` | End-to-end tests | — | 0 — empty scaffolding |
| `tests/performance` | Performance-oriented tests, separate from correctness suite | Yes | 1 |
| `tests/services/jupiter_crawler` | Regression tests for the Júpiter course-data crawler, replayed against a cached HTML+JSON snapshot (`tests/data/jupiter/`) | No (replay only — see below) | 1 |
| `tests/services/janus_crawler` | Same, for the postgraduate Janus crawler (`tests/data/janus/`) | No (replay only) | 1 |
| `tests/` (root) | Initial-data script test | Mixed | 1 |

Both crawler test files replay a **cached** snapshot — no network calls during a normal run. `tests/services/jupiter_crawler/test_jupiter_crawler.py` does have one lazy exception: if the current semester (JupiterWeb resets its offerings every semester) has no snapshot yet, it live-fetches a candidate once, saves it as an unreviewed `pending/` snapshot, and fails with instructions to review + promote it (`tests/scripts/promote_jupiter_snapshot.py`) — see `tests/services/jupiter_crawler/crawler_test_utils.py::ensure_fresh_snapshot`. Janus isn't semester-scoped, so its snapshot (`tests/data/janus/snapshots/`) is refreshed only manually, via `tests/scripts/generate_janus_snapshot.py` — no automatic staleness check.

## 4. Fixtures (`tests/conftest.py`)

Dependency order: `apply_migrations` (autouse, session-scoped) → `session` (per-test, truncate-on-teardown) → `user` (the seeded first-superuser admin) / `restricted_user` / `common_user` → `building` (also creates its main `Group`) → `group` (adds `restricted_user` to the building's main group) → `classroom` → `allocated_classroom` (creates a second classroom and allocates the standard `class_`'s first schedule into it — **don't reuse `class_` in allocation tests that also use this fixture**, per its docstring) → `subject` → `class_` → `meeting` / `exam` / `event`.

Four `TestClient` fixtures, each overriding `authenticate`/`google_token_authenticate` via `app.dependency_overrides`: `client` (admin `user`), `restricted_client` (`restricted_user`), `common_client` (`common_user`, no building/group), `public_client` (no auth override at all).

## 5. Factories (`tests/factories/`)

- `tests/factories/model/*` — SQLModel factories for DB-backed test data: `building`, `class_`, `classroom`, `event`, `exam`, `group`, `meeting`, `reservation`, `schedule`, `solicitation`, `subject`, `user`. **No `OccurrenceModelFactory` exists** — occurrences are only ever created indirectly, either via `OccurrenceRepository.allocate_schedule` (as in the `allocated_classroom` fixture) or by constructing `Occurrence(...)` directly in a test (as done in this round's new tests).
- `tests/factories/request/*` — HTTP request-payload builders, one per resource, mirroring the model factories.
- `tests/factories/response/*` — currently empty.
- `tests/factories/base/*` — shared `BaseFactory`/`BaseModelFactory`/`BaseRequestFactory` plus per-resource "base" factories providing Faker-driven default field values.

## 6. Current metrics

<!-- METRICS:START -->
<!-- Auto-generated by tests/scripts/update_test_metrics.py — do not hand-edit
     the table below; edit the script instead. Everything outside the
     METRICS:START/END markers is untouched by the script. -->

Baseline as of **2026-08-27**.

| Metric | Value |
|---|---|
| Test files | 60 |
| Test functions | 415 |
| Line coverage | 71.53% (12,249 statements, 3,487 missed) |
| Branch coverage | 39.39% (1,734 branches, 1,051 fully missed, 169 partial) |
| Combined coverage (line + branch) | 67.55% |
| Repository test-file ratio | 5 / 38 |
| Service test-file ratio | 7 / 15 |
| Last full run | 512 passed, 0 failed, 0 deselected |

The failure/skip counts above are whatever the run produced — check §7 to see which ones are pre-existing/known issues versus new regressions.
<!-- METRICS:END -->

Re-run `python tests/scripts/update_test_metrics.py` (see §9) to refresh this section — treat these numbers as a snapshot, not something guaranteed current.

## 7. What's untested (and known-failing tests)

**Known failing test** (pre-existing, not introduced by this round, out of scope to fix here): `tests/api/admin/test_user_admin_routes.py::test_delete_user_with_admin_user` fails with `DID NOT RAISE NoResultFound` — `DELETE /admin/users/{id}` returns `200 OK` but does not actually delete the user row. Worth a dedicated look before relying on that endpoint.

**Crawler snapshot tests** (`tests/services/{jupiter,janus}_crawler/`): previously 100% broken (stale pickled snapshots from a prior semester, no staleness detection) — now fixed. Both crawlers replay a JSON+HTML snapshot under `tests/data/{jupiter,janus}/`; Jupiter's snapshot is semester-labeled and lazily/automatically refreshed-to-`pending/` on rollover (review-gated — see §3); Janus's is flat and manually refreshed only (`tests/scripts/generate_janus_snapshot.py`), since postgrad offerings aren't semester-scoped. `tests/data/jupiter/subject_codes.txt` currently has several codes that fail to parse (`Error processing X: list index out of range`, likely subjects not offered this semester) — those are simply skipped when generating the snapshot, not included in the parametrized test cases.

**Repositories with no dedicated test file** (24 of 26 with tests below excluded): `allocation_log_repository`, `bug_report_evidence_repository`, `bug_report_repository`, `calendar_repository`, `class_repository`, `course_options_repository`, `course_repository`, `curriculum_repository`, `curriculum_subject_repository`, `event_repository`, `exam_repository`, `feedback_repository`, `forum_repository`, `holiday_category_repository`, `holiday_repository`, `institutional_event_repository`, `intentional_conflict_repository`, `meeting_repository`, `mobile_comments_repository`, `mobile_user_repository`, `reservation_repository`, `schedule_repository`, `solicitation_repository`, `subject_repository`, `user_schedule_repository`, `user_session_repository`.

**Services with no dedicated test file**: `gmail_service`, `conflict_checker` (its `ConflictChecker` orchestration class — this round only covers the `Occurrence` model layer beneath it, plus two focused route-level tests; the class itself, including its intentional-conflict pairing logic, remains untested as a unit), `occupance_reports_service`, and every file in `server/services/security/` (`buildings_permission_checker`, `classrooms_permission_checker`, `class_permission_checker`, `exam_permission_checker`, `group_permission_checker`, `occurrence_permission_checker`, `reservation_permission_checker`, `schedule_permission_checker`, `solicitation_permission_checker`, `subjects_permission_checker`, `base_permission_checker`).

**Empty scaffolding directories**: `tests/api/public`, `tests/e2e`, `tests/integration/services`, `tests/unit/services`, `tests/unit/utils`.

Recommended next priority: `ConflictChecker` (highest business-risk, zero coverage of its own orchestration logic) and `server/services/security/*` (authorization-critical, zero coverage).

## 8. Metrics glossary — what to track and why

- **Line coverage** — % of executable lines run by the suite. Cheap, the first thing `--cov-report=term-missing` shows. Weakest signal on its own: it doesn't prove every branch of a conditional was exercised.
- **Branch coverage** (`branch = true`) — % of both sides of every `if`/`and`/`or` actually taken. A stronger signal, and specifically relevant here: `Occurrence.conflicts_with_time`'s `and`, `ConflictParams.validate_body`'s dozen mutually-exclusive `if` branches, and `ConflictChecker`'s intentional-vs-unintentional conflict branching are exactly the kind of logic where line coverage can look deceptively high while whole branches are never hit.
- **Per-tier test counts** (§3's table) — a proxy for the test pyramid's shape. Today it's bottom-heavy toward `api/*` (full HTTP round-trips through a real DB) and nearly empty at `unit/*` — meaning most logic is only verified indirectly through the API layer, which is a slower feedback loop than a focused unit test.
- **Repository/service test-file ratio** (§6) — coarse but concrete: "does this module have *any* dedicated verification at all," independent of what % of lines within it are covered.
- **Not yet tracked, worth considering later**: a `--cov-fail-under` CI gate (deliberately not added yet — set one only after deciding on a realistic floor, not blindly at the current baseline); mutation testing (would catch assertions that pass but don't actually verify behavior); flaky-test rate; test suite execution time trends.

## 9. Conventions for adding new tests

- No-DB, pure-logic test → `tests/unit/{models,services,utils}/`. See `tests/unit/models/test_occurrence_model.py` for the `make_x()`-helper + module-docstring pattern.
- DB-backed but no HTTP layer → `tests/integration/{repositories,services}/`, using the `session` fixture directly.
- Full HTTP route test → `tests/api/{admin,authenticated,public,restricted}/`, using the matching `*_client` fixture for the route's auth tier.
- Reuse existing fixtures/factories (§4, §5) before adding new ones. If a new factory is genuinely needed (e.g. the still-missing `OccurrenceModelFactory`), follow `tests/factories/base/base_model_factory.py`'s pattern.

After adding/removing tests, refresh §6 with:

```bash
poetry run python tests/scripts/update_test_metrics.py
```

This runs the full suite, regenerates `coverage.json`, and rewrites only the auto-generated table in §6 above — everything else in this file is left untouched. Commit the resulting `TESTS.md` diff alongside your test changes.
