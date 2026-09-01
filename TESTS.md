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
| `tests/api/admin` | Full HTTP tests for admin-only routes, via the `client` fixture | Yes (DB + `TestClient`) | 5 |
| `tests/api/authenticated` | HTTP tests for routes requiring any logged-in user | Yes | 3 |
| `tests/api/public` | HTTP tests for no-auth/optional-auth routes — every `server/routes/public/*.py` file now has a matching test file | Yes | 20 |
| `tests/api/restricted` | HTTP tests for routes requiring admin-or-group-member | Yes | 6 |
| `tests/integration/repositories` | DB-backed repository tests, no HTTP layer | Yes (DB only) | 18 |
| `tests/integration/deps/repository_adapters` | DB-backed tests for the FastAPI-DI "repository adapter" layer (`server/deps/repository_adapters/*.py`), constructed directly (bypassing FastAPI's DI) via the same dependency-provider functions the framework would call | Yes (DB only) | 10 |
| `tests/integration/services` | DB-backed service-layer tests, plus `tests/integration/services/security/` mirroring `server/services/security/` (one file per checker) | Yes | 3 + 10 in `security/` |
| `tests/unit/models` | Pure-Python model-logic tests, no DB/session, including `tests/unit/models/{requests,responses}/` | No | 21 |
| `tests/unit/services` | Pure-Python service-logic tests, plus `tests/unit/services/security/` for the one security file that's DB-free | No | 3 + 1 in `security/` |
| `tests/unit/utils` | Pure-Python utility tests | No | 8 |
| `tests/unit/deps` | Pure-Python dependency-provider tests | No | 1 |
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

- `tests/factories/model/*` — SQLModel factories for DB-backed test data, one per aggregate (`building`, `class_`, `classroom`, `course`, `curriculum`, `event`, `exam`, `group`, `meeting`, `mobile_user`, `occurrence`, `reservation`, `schedule`, `solicitation`, `subject`, `user`, plus the `*_permission_model_factory.py` family).
- `tests/factories/request/*` — HTTP request-payload builders, one per resource, mirroring the model factories.
- `tests/factories/response/*` — currently empty.
- `tests/factories/base/*` — shared `BaseFactory`/`BaseModelFactory`/`BaseRequestFactory` plus per-resource "base" factories providing Faker-driven default field values.

### 5.1 The dict/factory layering

Every resource that has a factory is backed by four small pieces, split across `server/models/dicts/` (the type layer, shipped in the main package because production code — e.g. repository `update()` signatures — also uses these dicts) and `tests/factories/` (the construction layer):

1. **Base dict** — `server/models/dicts/base/<resource>_base_dict.py`. A `TypedDict(BaseDict, total=False)` listing the resource's "business" fields only — no `id`, no timestamps, no FKs, no relationships. Example, `MobileUserBaseDict`:
   ```python
   class MobileUserBaseDict(BaseDict, total=False):
       sub: str
       email: str
       given_name: str
       family_name: str
       picture_url: str | None
   ```
2. **Model dict** — `server/models/dicts/database/<resource>_database_dicts.py`. A `TypedDict(BaseModelDict, <Resource>BaseDict, total=False)` that adds whatever the DB layer needs on top of the base dict: FK id columns (`*_id`), `created_at`/`created_by_id`/`updated_at`/`updated_by_id`, and relationship attributes (e.g. `course: Course`, `subjects: list[CurriculumSubject]`). `BaseModelDict` itself just contributes `id: int | None`. **Only include a relationship field here if the SQLModel actually declares a `Relationship()` for it** — e.g. `Course` only has `created_by_id`, no `created_by` relationship, so `CourseModelDict` must not invent one.
3. **Base factory** — `tests/factories/base/<resource>_base_factory.py`. A `BaseFactory` subclass with **no session**. Its only job is `get_base_defaults() -> <Resource>BaseDict`, filling every base-dict field via `self.faker` (the module-level `shared_faker = Faker("pt_BR")`, shared across all factories so `.unique.xxx()` dedupes correctly within a test — see the comment in `tests/factories/base/base_factory.py`). Fixed, non-Faker values are fine here too when a field's exact value doesn't matter to any test (e.g. `OccurrenceBaseFactory` hardcodes `8:00–10:00`).
4. **Model factory** — `tests/factories/model/<resource>_model_factory.py`. A `BaseModelFactory[Model]` subclass (session-bound). `get_defaults()` calls `self.core_factory.get_base_defaults()` and layers on FK ids (typically via `must_be_int(dependency.id)`) and relationship objects, using whatever the constructor was given (e.g. `CourseModelFactory(creator: User, session: Session)`). This is the only layer that knows about other models/relationships.

`BaseModelFactory` (`tests/factories/model/base_model_factory.py`) is `Generic[M]` and provides, on top of `get_defaults()`:
- `build(**overrides) -> M` — instantiates `Model(**{**defaults, **overrides})` and returns it **without touching `self.session`** (no `add()`/`commit()`/`refresh()`). Safe to call with an unbound `Session()` in a pure unit test. Use this when the test never needs the row to be queryable — it only needs a correctly-shaped, correctly-related in-memory object graph.
- `create(**overrides) -> M` / `create_and_refresh(**overrides) -> M` — same instantiation, but `add()`s (and, for the `_and_refresh` variant, `commit()`s + `refresh()`es) the model against `self.session`. Use these in integration/API tests that need a real, persisted, queryable row.
- `create_many*` / `update*` / `get_by_id` — see the source; same instantiate-then-optionally-persist shape.

**Overrides only replace keys that already exist in `get_defaults()`'s dict** (`__update_default_dict` skips unknown keys silently) — if a base dict is missing a field entirely, an override for it is a silent no-op, not an error. When adding a field to a model that tests need to override, make sure it's actually present in the base/model dict, or the override will appear to do nothing (see `ClassroomBaseFactory`'s missing `remote` field as a cautionary example — worked around at the call site rather than changing the shared factory's defaults).

**`.build()` is not automatically session-free for every factory** — it's only as session-free as `get_defaults()` is. `ExamModelFactory`/`EventModelFactory`'s `get_defaults()` call `self.reservation_factory.create_and_refresh()` internally (a real DB write), so `.build()` on those factories still hits the database. Don't assume session-freedom; check `get_defaults()` before relying on `.build()` in a no-DB unit test.

**FK columns don't sync from relationship assignment without a flush.** Assigning `class_.subject = subject` does not backfill `class_.subject_id` until the session flushes/commits — irrelevant for `create()`/`create_and_refresh()` (which do flush), but it means DB-free helpers built on `.build()` must manually patch `.id` on each built object (`model.id = next(_next_id)`, since nothing ever assigns a real DB id) immediately after building it, in dependency order, and either rely on a `get_defaults()` that already computes the FK via `must_be_int(dependency.id)`, or set the FK column by hand afterward.

### 5.2 DB-free vs DB-backed test-utils files

`tests/utils/*_test_utils.py` hold shared `make_*` helpers so tests don't redeclare local builders. Two flavors coexist, both delegating to the factories above rather than hand-rolling models:
- **DB-free** (`tests/utils/academic_test_utils.py`, `tests/utils/time_test_utils.py`) — for pure `tests/unit/*` tests. Each `make_*` calls `XxxModelFactory(session=Session(), ...).build(...)`, patches `.id`, and wires any FK the factory's `get_defaults()` doesn't already compute. A local `_given(**kwargs)` helper drops `None`-valued kwargs so an unset caller argument falls through to the factory's Faker default instead of overriding it with `None`.
- **DB-backed** (`tests/utils/mobile_user_test_utils.py`, `tests/utils/curriculum_test_utils.py`) — for `tests/api/*`/`tests/integration/*` tests that need a real, queryable row. Each `make_*` calls `XxxModelFactory(session=session).create_and_refresh(...)`, taking the real `session` fixture as a parameter rather than constructing its own.

Don't merge the two into one file/flavor: which one a helper belongs in is determined by whether its callers need persistence, not by convenience.

## 6. Current metrics

<!-- METRICS:START -->
<!-- Auto-generated by tests/scripts/update_test_metrics.py — do not hand-edit
     the table below; edit the script instead. Everything outside the
     METRICS:START/END markers is untouched by the script. -->

Baseline as of **2026-08-31**.

| Metric | Value |
|---|---|
| Test files | 162 |
| Test functions | 1258 |
| Line coverage | 86.97% (12,551 statements, 1,636 missed) |
| Branch coverage | 68.34% (1,734 branches, 549 fully missed, 183 partial) |
| Combined coverage (line + branch) | 84.70% |
| Repository test-file ratio | 21 / 38 |
| Service test-file ratio | 13 / 15 |
| Last full run | 1355 passed, 2 failed, 0 deselected |

The failure/skip counts above are whatever the run produced — check §7 to see which ones are pre-existing/known issues versus new regressions.
<!-- METRICS:END -->

Re-run `python tests/scripts/update_test_metrics.py` (see §9) to refresh this section — treat these numbers as a snapshot, not something guaranteed current.

## 7. What's untested (and known-failing tests)

**Known failing test** (pre-existing, not introduced by this round, out of scope to fix here): `tests/api/admin/test_user_admin_routes.py::test_delete_user_with_admin_user` fails with `DID NOT RAISE NoResultFound` — `DELETE /admin/users/{id}` returns `200 OK` but does not actually delete the user row. Worth a dedicated look before relying on that endpoint.

**Crawler snapshot tests** (`tests/services/{jupiter,janus}_crawler/`): previously 100% broken (stale pickled snapshots from a prior semester, no staleness detection) — now fixed. Both crawlers replay a JSON+HTML snapshot under `tests/data/{jupiter,janus}/`; Jupiter's snapshot is semester-labeled and lazily/automatically refreshed-to-`pending/` on rollover (review-gated — see §3); Janus's is flat and manually refreshed only (`tests/scripts/generate_janus_snapshot.py`), since postgrad offerings aren't semester-scoped. `tests/data/jupiter/subject_codes.txt` currently has several codes that fail to parse (`Error processing X: list index out of range`, likely subjects not offered this semester) — those are simply skipped when generating the snapshot, not included in the parametrized test cases.

**Repositories with no dedicated test file** (20 of 38; `building_repository`, `classroom_repository`, `permission_repository`, `role_repository`, `user_repository`, `user_schedule_repository`, `user_session_repository`, `event_repository`, `meeting_repository`, `exam_repository`, `reservation_repository`, `solicitation_repository`, `class_repository`, `schedule_repository`, `subject_repository`, `occurrence_repository`, `group_repository`, `intentional_conflict_repository` have one — see `BUGS_FOUND.md` for real bugs caught while writing the `user`/`reservation` ones): `allocation_log_repository`, `api_access_log_repository`, `api_incident_report_repository`, `bug_report_evidence_repository`, `bug_report_repository`, `building_permission_repository`, `calendar_repository`, `classroom_permission_repository`, `course_options_repository`, `course_permission_repository`, `course_repository`, `curriculum_repository`, `curriculum_subject_repository`, `feedback_repository`, `forum_repository`, `holiday_category_repository`, `holiday_repository`, `institutional_event_repository`, `mobile_comments_repository`, `mobile_user_repository`.

**Services with no dedicated test file**: `gmail_service` and `conflict_checker` (its `ConflictChecker` orchestration class — the `Occurrence` model layer beneath it and two focused route-level tests are covered, but the class itself, including its intentional-conflict pairing logic, remains untested as a unit). `server/services/security/*` — the authorization/permission-checker layer — is well covered (see the `tests/{integration,unit}/services/security/` mirror in §3's table above), with the single exception of `base_permission_checker.py`, a two-line abstract stub (`check_permission` just raises `NotImplementedError`) that every concrete checker overrides; not worth a dedicated test on its own.

**Empty scaffolding directories**: `tests/e2e`.

Recommended next priority: `ConflictChecker` (highest business-risk, zero coverage of its own orchestration logic) — `server/services/security/*` is already well covered (see above).

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
- **When `server/` groups a set of files into a subpackage** (e.g. `server/services/security/*`), mirror that as a subfolder under the matching test tier — `tests/integration/services/security/`, `tests/unit/services/security/` — rather than flattening everything under `tests/integration/services/`. Pick the subfolder's tier (`integration` vs `unit`) per file the normal way (does it touch `session`/the DB or not), so a subpackage can legitimately end up split across both, as `server/services/security/` currently is.
- Reuse existing fixtures/factories (§4, §5) before adding new ones.

### 9.1 Test data protocol

Follow this checklist **every time a test needs to create a DB model instance** (whether it ends up committed or not), instead of hand-constructing the model inline:

1. **Do you need a factory at all?** If the test can use an existing `tests/conftest.py` fixture (`user`, `building`, `classroom`, `subject`, `class_`, `meeting`, `exam`, `event`, etc. — see §4), prefer that over building your own instance.
2. **Does a factory for this model already exist?** Check `tests/factories/model/` for `<Resource>ModelFactory`. If yes, reuse it — don't write a new local `make_*`/inline constructor for a model that already has one.
3. **Pick the right construction mode**:
   - Need the row queryable via `session`/HTTP (integration or API test) → `XxxModelFactory(session=session, ...).create()` or `.create_and_refresh()`.
   - Pure unit test, no DB touch wanted → `XxxModelFactory(session=Session(), ...).build(...)`, then manually patch `.id = next(_next_id)` and any FK column the factory's `get_defaults()` doesn't already derive (see §5.1's FK-sync note). First confirm the factory's `get_defaults()` doesn't itself call `create()`/`create_and_refresh()` on a nested factory (as `ExamModelFactory`/`EventModelFactory` do) — if it does, `.build()` isn't actually session-free and you should construct the model directly instead (see `make_exam` in `tests/utils/academic_test_utils.py` for the pattern).
   - Put the resulting helper in the matching `tests/utils/*_test_utils.py` file (DB-free vs DB-backed, per §5.2) rather than as a test-local function, so other tests can reuse it.
4. **If no factory exists yet**, create the full stack following §5.1's pattern: base dict (`server/models/dicts/base/`) → model dict (`server/models/dicts/database/`) → base factory (`tests/factories/base/`, Faker-driven via `self.faker`) → model factory (`tests/factories/model/`, `BaseModelFactory[Model]` subclass). Don't skip layers (e.g. don't put Faker defaults directly in the model factory) — the split is what lets `.build()` and `.create()` share the exact same default logic.

After adding/removing tests, refresh §6 with:

```bash
poetry run python tests/scripts/update_test_metrics.py
```

This runs the full suite, regenerates `coverage.json`, and rewrites only the auto-generated table in §6 above — everything else in this file is left untouched. Commit the resulting `TESTS.md` diff alongside your test changes.
