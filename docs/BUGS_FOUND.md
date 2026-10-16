# BUGS_FOUND.md

Bugs discovered while writing tests for existing (previously untested or under-tested) code, rather than while implementing a new feature. Each entry records what was wrong, why it mattered, and the fix applied alongside the test that caught (or now guards) it. See `TESTS.md` for the overall test suite structure and conventions.

## Authentication & authorization

### Google Workspace domain check used `and` instead of `or`, letting unverified emails skip the domain check

**Found while**: adding coverage for the public routes / auth-adjacent utilities.

**File**: `server/utils/google_auth_utils.py`

**Bug**: `authenticate_with_google` was supposed to reject a login unless the account is on an allowed Workspace domain **and** has a verified email. It was written the other way around:

```python
if idInfo["hd"] not in CONFIG.allowed_gmails_domains and idInfo["email_verified"]:
    raise ValueError("Wrong domain name.")
```

With `and`, the rejection only fires when *both* conditions are true (wrong domain **and** verified email). If the email was unverified (`email_verified: False`), the whole expression short-circuited to `False` and the function let the login through regardless of domain — i.e. an unverified email from *any* domain, including one outside `allowed_gmails_domains`, bypassed the domain restriction entirely.

**Risk**: this is the core gate that decides who is allowed into the system via Google login. The intended policy ("must be on an allowed domain, and Google must have verified the email") was silently weakened to "either condition can be missing, as long as it isn't both" — the domain allowlist had a live bypass for any unverified Google account. This is an authentication/authorization bug, not just a data-correctness one.

**Fix**: invert to `or`, matching the intended "reject if either check fails" policy:

```python
if idInfo["hd"] not in CONFIG.allowed_gmails_domains or not idInfo["email_verified"]:
    raise ValueError("Wrong domain name.")
```

**Caught by**: `tests/unit/utils/test_google_auth_utils.py`, which exercises the domain/verified-email matrix directly (wrong domain, unverified email, both, neither) against `authenticate_with_google`.

---

### Google auth failures leaked as unhandled 500s instead of 401s (mobile auth + forum routes)

**Found while**: adding route tests for `mobile_google_authentication_routes.py` and `forum_routes.py`.

**Files**: `server/routes/public/mobile_google_authentication_routes.py`, `server/routes/public/forum_routes.py`, `server/repositories/mobile_user_repository.py`

**Bug**: three separate route handlers called Google-auth logic directly inline and let its failure modes propagate unhandled:

- `authenticate_user` raised a bare `ValueError("Invalid idToken")` when the `idToken` header was missing. FastAPI has no handler registered for plain `ValueError`, so this became an unhandled 500 instead of a 4xx.
- The same handler called `MobileUserRepository.get_user_by_sub(sub=sub, session=session)`, which used `.one()` and therefore raised `NoResultFound` (also unhandled → 500) for the extremely common case of a **first-time user who isn't in the DB yet** — even though the route's own docstring says it should just report "not registered", not crash.
- `create_new_user` bypassed the shared auth logic altogether and called the Google SDK (`id_token.verify_oauth2_token`) directly with a *different* client ID (`google_auth_mobile_client_id`) than the one used elsewhere, so the two "mobile auth" endpoints verified tokens through two different, inconsistent code paths — and the domain/verified-email check above didn't apply to it at all.
- `forum_routes.py`'s `create_forum_post`, `delete_forum_post`, and `create_forum_post_reply` each called `authenticate_with_google(authorization)` inline as a side-effecting statement; a failed check raised the same bare `ValueError`, again surfacing as an unhandled 500 instead of a 401.

**Risk**: every one of these is a "the feature is completely broken for the exact case it exists to handle" bug — a first-time mobile user hitting `/mobile/authentication` (the *normal* path for someone who hasn't registered yet) got a 500 instead of the "not registered" response the endpoint is documented to return; a missing/invalid token on any of the four affected endpoints returned an opaque 500 instead of a meaningful 401, which is worse for clients (can't distinguish "your token is bad" from "our server is broken") and worse for on-call (500s page, expected 401s don't). The `create_new_user` split-verification-path issue also meant a security fix to the shared domain check (see above) silently didn't apply everywhere tokens were checked.

**Fix**: centralized Google-token verification into two FastAPI dependencies (`server/deps/google_auth_dep.py`) that catch `ValueError` and re-raise it as a proper `HTTPException` (401):

```python
class InvalidGoogleIdToken(HTTPException):
    def __init__(self, detail: str = "Invalid idToken") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

def google_id_token_authenticate(idToken: Annotated[str, Header()]) -> Any:
    try:
        return authenticate_with_google(idToken)
    except ValueError as exc:
        raise InvalidGoogleIdToken(str(exc)) from exc

def google_authorization_authenticate(authorization: str = Header(None)) -> Any:
    try:
        return authenticate_with_google(authorization)
    except ValueError as exc:
        raise InvalidGoogleIdToken(str(exc)) from exc
```

`mobile_google_authentication_routes.py`'s two endpoints now depend on `GoogleIdTokenDep` (both go through the same `authenticate_with_google` path, including `create_new_user`, closing the inconsistent-verification gap); `forum_routes.py`'s three write endpoints now depend on `GoogleAuthorizationDep` instead of calling `authenticate_with_google` inline. A new `MobileUserRepository.get_user_by_sub_or_none` (using `.first()` instead of `.one()`) replaced the crashing lookup in `authenticate_user`, so an unregistered sub now correctly produces `is_registered_user: False` instead of a 500.

**Caught by**: `tests/api/public/test_mobile_google_authentication_routes.py` (registered user, unregistered user, invalid token → 401) and `tests/api/public/test_forum_routes.py`'s auth-failure cases on create/delete/reply.

---

## Response models

### `EventResponse.from_event` / `MeetingResponse.from_meeting` crashed on every call because of `super()` inside a `@classmethod`

**Found while**: adding route tests that exercise `/reservations/events` and `/reservations/meetings`.

**Files**: `server/models/http/responses/event_response_models.py`, `server/models/http/responses/meeting_response_models.py`

**Bug**: both subclasses built their "base" object by calling `super()` instead of naming the parent class directly:

```python
class EventResponse(EventResponseBase):
    reservation: ReservationCoreResponse

    @classmethod
    def from_event(cls, event: Event) -> Self:
        base = super().from_event(event)   # <- the bug
        return cls(
            **base.model_dump(),
            reservation=ReservationCoreResponse.from_reservation(event.reservation),
        )
```

The subtlety: `super()` changes *where Python starts looking up the method* (`EventResponseBase.from_event`), but it does **not** change what `cls` is bound to inside that method body — `cls` is still whatever the *original* call was made on, i.e. `EventResponse`. So `super().from_event(event)` actually executes `EventResponseBase.from_event`'s body, but with `cls = EventResponse`:

```python
@classmethod
def from_event(cls, event: Event) -> Self:
    return cls(id=..., reservation_id=..., link=..., type=...)   # cls is EventResponse here!
```

`EventResponse` additionally requires a `reservation` field that this call never provides, so `cls(id=..., reservation_id=..., link=..., type=...)` immediately raised a Pydantic `ValidationError` ("field required: reservation") — every single call to `EventResponse.from_event` (and the `Meeting` equivalent) failed. This is a case where `super()` inside a `@classmethod` does *not* behave like "call the parent class's version of this with the parent as the type" the way instance methods usually feel like they do — it's a common enough gotcha that it's worth calling out explicitly rather than reaching for `super()` by habit in a classmethod that's about to reconstruct `cls`.

**Risk**: this wasn't a subtle data bug, it was a hard crash — `GET /reservations/events` and `GET /reservations/meetings` returned a 500 on every request that had at least one row to serialize, for as long as this code existed. Total endpoint outage, not degraded behavior.

**Fix**: call the base class by name instead of via `super()`, so `cls` inside `EventResponseBase.from_event` is genuinely `EventResponseBase`:

```python
base = EventResponseBase.from_event(event)
```

(same fix applied to `MeetingResponse.from_meeting` → `MeetingResponseBase.from_meeting`). The other classmethod builders in this codebase (`ExamResponse.from_exam`, `ClassResponse.from_class`, etc.) already followed this by-name pattern — `EventResponse`/`MeetingResponse` were the only two written with `super()`.

**Caught by**: `tests/unit/models/responses/test_event_response_models.py` and `tests/unit/models/responses/test_meeting_response_models.py`, which call `.from_event()`/`.from_meeting()` directly and assert the returned response's fields — these fail immediately (Pydantic `ValidationError`) against the old code.

---

### Mobile class listing's date-interval filter was inverted (and computed twice, with the first result thrown away)

**Found while**: adding route tests for the mobile class-listing endpoint.

**File**: `server/models/http/responses/mobile_class_response_models.py`

**Bug**: two issues stacked in the same block of `MobileClassResponse.from_class`:

1. **Dead code**: the interval-filtering `if interval: ...` block ran once, producing a filtered `schedules` list — which was then immediately discarded by a `schedules = _class.schedules` reset right after it, before the *same* filtering block ran a second time. The first pass was pure wasted computation with no effect on the result, a sign of an accidental duplicate/paste.
2. **Inverted comparison**: in the (only effective) second pass, the range-filter condition was backwards:
   ```python
   schedules = [
       schedule
       for schedule in schedules
       if interval.start >= schedule.start_date
       and schedule.end_date <= interval.end
   ]
   ```
   `interval.start >= schedule.start_date` means "the schedule started on or before the interval's start" — combined with `end_date <= interval.end`, this only matched schedules that started *before* the requested window even opened and also happened to end inside it. A schedule that starts normally *within* the requested date range (the overwhelmingly common case for "show me classes happening between date A and date B") was excluded.

**Risk**: this is the filter behind the mobile app's date-ranged class listing. With the comparison inverted, a normal query for "classes in this date range" returned close to the opposite of the intended set — classes that started before the range and (coincidentally) ended inside it, while excluding classes that actually run during the requested window. Not a crash, so it would have been easy to ship and only notice as "the mobile app is showing wrong/missing classes for this date range" without an obvious root cause.

**Fix**: removed the dead first pass, and corrected the comparison direction to match "schedule falls within the requested range":

```python
schedules = [
    schedule
    for schedule in schedules
    if schedule.start_date >= interval.start
    and schedule.end_date <= interval.end
]
```

**Caught by**: `tests/api/public/test_mobile_classes_routes.py`'s interval-filtering cases, which build schedules starting inside vs. outside a requested `start`/`end` range and assert which ones come back.

---

## Repositories

### `UserRepository.get_admin_users` never returned any admin users

**Found while**: writing `tests/integration/repositories/test_user_repository.py`.

**File**: `server/repositories/user_repository.py`

**Bug**: the method built its query with a Python identity check instead of a SQLModel/SQLAlchemy column comparison:

```python
statement = select(User).where(User.is_admin is True)
```

`User.is_admin is True` is evaluated by Python *before* SQLAlchemy ever sees it — `User.is_admin` is a mapped column descriptor object, which is never the same object as the literal `True`, so the expression always evaluates to the plain Python value `False`. The resulting call is effectively `select(User).where(False)`, which SQLAlchemy compiles into a statement that can never match a row. The method silently returned an empty list for every call, regardless of how many admin users existed in the database.

**Risk**: `get_admin_users` had no callers elsewhere in the codebase at the time this was found, so it was not causing a live incident. The risk is entirely latent: the first feature built on top of it (e.g. "notify all admins", an admin-only digest, a dashboard count of admins) would silently receive an empty list instead of an error, which is the worst failure mode for this kind of bug — no exception, no log line, just quietly wrong data. The same `is True` / `is False` mistake is easy to reintroduce elsewhere since it is syntactically valid Python and produces no type error.

**Fix**: use a proper column-boolean comparison via `col(...)`, matching the pattern used everywhere else in this repository:

```python
statement = select(User).where(col(User.is_admin))
```

**Caught by**: `test_get_admin_users_returns_only_admin_users`, which creates one admin user (the `admin_user` fixture) and one non-admin user (`common_user`) and asserts the admin appears in the result while the non-admin does not. This test failed against the original code (returned an empty list) and passes against the fix.

---

### `ReservationRepository.get_by_id_on_buildings` crashed on every call

**Found while**: writing `tests/integration/repositories/test_reservation_repository.py`.

**File**: `server/repositories/reservation_repository.py`

**Bug**: the query joined straight from `Reservation` to `Classroom` to `Building` with no ON clause and no intermediate `Schedule`:

```python
statement = (
    select(Reservation)
    .join(Classroom)
    .join(Building)
    .where(col(Building.id).in_(building_ids))
    .where(col(Reservation.id) == id)
)
```

`Reservation` has no direct foreign key or relationship to `Classroom` — the only path is `Reservation → Schedule → Classroom → Building` (which is exactly what the sibling method `get_all_on_buildings`, four lines away in the same file, does correctly with explicit `ON` conditions). With no relationship for SQLAlchemy to infer a join from and no explicit condition supplied, calling this method doesn't return zero rows — it raises `sqlalchemy.exc.InvalidRequestError: Don't know how to join to <Mapper ... Classroom>` immediately, every time.

**Risk**: no code in the codebase calls this method today, so it wasn't an active incident — but that also means the bug was invisible until now: nothing would have caught it until the first caller was added, at which point it would 500 on its very first real request in whatever new feature reached for it.

**Fix**: route the join through `Schedule`, matching `get_all_on_buildings`'s pattern:

```python
statement = (
    select(Reservation)
    .join(Schedule, col(Schedule.reservation_id) == col(Reservation.id))
    .join(Classroom, col(Schedule.classroom_id) == col(Classroom.id))
    .join(Building, col(Classroom.building_id) == col(Building.id))
    .where(col(Building.id).in_(building_ids))
    .where(col(Reservation.id) == id)
)
```

**Caught by**: `TestGetByIdOnBuildings::test_returns_the_reservation_when_its_building_matches`, which failed with the `InvalidRequestError` above against the original code.

---

### `ReservationRepository.get_by_id_on_classrooms` ignored the `id` it was asked for

**Found while**: writing `tests/integration/repositories/test_reservation_repository.py`, immediately after the bug above in the same file.

**File**: `server/repositories/reservation_repository.py`

**Bug**: the method takes an `id` parameter and is named `get_by_id_on_classrooms`, but its query never filtered on that `id` — only on `classroom_ids`:

```python
def get_by_id_on_classrooms(
    *, id: int, classroom_ids: list[int], session: Session
) -> Reservation:
    statement = (
        select(Reservation)
        .join(Schedule, col(Schedule.reservation_id) == col(Reservation.id))
        .join(Classroom, col(Classroom.id) == col(Schedule.classroom_id))
        .where(
            col(Classroom.id).in_(classroom_ids),
        )
    )
    reservation = session.exec(statement).one()   # .one() over ALL reservations in these classrooms
```

With exactly one reservation in the given classrooms this happens to return the right row by accident. With more than one — the normal case for any classroom that's been booked more than once — `.one()` raises `MultipleResultsFound`, which isn't caught by the method's `except NoResultFound` handler, so it propagates as an unhandled 500 instead of either returning the requested reservation or a clean "not found."

**Risk**: same as above — no current callers, so latent rather than active, but a caller checking "does reservation X belong to one of these classrooms" (the method's evident purpose, e.g. for a permission check) would get the *wrong* reservation back silently whenever it wasn't the only one in that classroom, or a 500 crash instead of a 404. A wrong reservation coming back from what looks like an authorization-scoping check is the worse of those two failure modes.

**Fix**: add the missing filter:

```python
.where(
    col(Classroom.id).in_(classroom_ids),
    col(Reservation.id) == id,
)
```

**Caught by**: `TestGetByIdOnClassrooms::test_does_not_return_a_different_reservation_in_the_same_classroom`, which creates two reservations in the same classroom and asserts that asking for the first one's `id` doesn't return the second — this would have failed (or thrown `MultipleResultsFound`) against the original code.

---

## Repository adapters

### `BuildingRepositoryAdapter.create` let a duplicate-name `IntegrityError` escape as an unhandled 500

**Found while**: writing `tests/integration/deps/repository_adapters/test_building_repository_adapter.py`.

**File**: `server/deps/repository_adapters/building_repository_adapter.py`

**Bug**: the adapter called `BuildingRepository.create(...)` outside its own `try/except IntegrityError` block:

```python
def create(self, input: BuildingRegister) -> Building:
    self.checker.check_creation_permission(BuildingAction.CREATE)
    building = BuildingRepository.create(
        building_in=input, creator=self.user, session=self.session
    )
    try:
        self.session.commit()
    except IntegrityError:
        self.session.rollback()
        raise BuildingAlreadyExists(input.name)
    ...
```

`BuildingRepository.create()` internally does `session.add(building); session.flush()` before returning, because it needs the new building's `id` to create its main `Group` in the same call. That `flush()` is what actually hits the DB and raises `IntegrityError` on a duplicate `name` — and it happens on the line *before* the `try:`, so the intended `except IntegrityError: raise BuildingAlreadyExists(...)` was dead code for this case.

**Risk**: creating a building with a name that already exists — a completely routine user mistake — crashed with an unhandled 500 instead of the documented 409 `BuildingAlreadyExists`, at the exact call site whose whole purpose is to catch that case.

**Fix**: move the repository call inside the `try` block, so the flush's `IntegrityError` is caught too:

```python
try:
    building = BuildingRepository.create(
        building_in=input, creator=self.user, session=self.session
    )
    self.session.commit()
except IntegrityError:
    self.session.rollback()
    raise BuildingAlreadyExists(input.name)
```

**Caught by**: `TestCreate::test_raises_on_duplicate_name`.

---

### `BuildingRepository.delete` / `ClassroomRepository.delete` crashed whenever the resource had a specific permission grant on it

**Found while**: writing `tests/integration/deps/repository_adapters/test_building_repository_adapter.py` and `test_classroom_repository_adapter.py`.

**Files**: `server/repositories/building_repository.py`, `server/repositories/classroom_repository.py`

**Bug**: `BuildingPermission.building_id` and `ClassroomPermission.classroom_id` are `Field(foreign_key=...)` with no `ondelete="CASCADE"`, at either the SQLModel or the Alembic-migration level. Neither `BuildingRepository.delete` nor `ClassroomRepository.delete` cleared these rows before deleting their resource, so deleting a building (or a classroom, including one that cascade-deletes as part of a building delete) that had ever had a specific, non-wildcard permission granted on it crashed with an unhandled `IntegrityError`/`ForeignKeyViolation` instead of a clean deletion.

**Risk**: this is exactly the state the in-progress role/permission system is meant to put resources into routinely — granting someone `READ`/`UPDATE`/etc. on one specific building or classroom. Any building or classroom that had ever received such a grant became permanently undeletable via the normal API, failing with a raw 500.

**Fix**: added a generic `get_by_ids` to the shared `PermissionRepository` base class (used by both `BuildingPermissionRepository` and `ClassroomPermissionRepository`) and call it from both `delete` methods to clear dangling permission rows first:

```python
# PermissionRepository
@classmethod
def get_by_ids(cls, *, resource_ids: list[int], session: Session) -> list[P]:
    model = TypeGuard.ensure_not_none(cls.model)
    resource_field = TypeGuard.ensure_not_none(cls.resource_field)
    column = getattr(model, resource_field)
    statement = select(model).where(column.in_(resource_ids))
    return list(session.exec(statement).all())
```

`BuildingRepository.delete` now also clears `ClassroomPermission` rows for every classroom that will cascade-delete with the building.

**Caught by**: `TestDelete::test_deletes_via_granted_permission` in both `test_building_repository_adapter.py` and `test_classroom_repository_adapter.py` (grant a permission on the exact resource being deleted, then delete it).

---

### `ClassroomRepositoryAdapter.delete` bypassed the repository's schedule-deallocation step

**Found while**: writing `tests/integration/deps/repository_adapters/test_classroom_repository_adapter.py`.

**File**: `server/deps/repository_adapters/classroom_repository_adapter.py`

**Bug**: the adapter reimplemented deletion inline (`self.session.delete(classroom)`) instead of calling `ClassroomRepository.delete()`, skipping that method's loop that deallocates every schedule assigned to the classroom first. `Schedule.classroom_id` also has no `ON DELETE CASCADE`, so deleting any classroom with an allocated schedule — a normal, common state, not an edge case — crashed with an unhandled `IntegrityError`.

**Risk**: deleting a classroom that currently has any class scheduled into it (the ordinary case for a real classroom, not a corner case) failed with a 500 instead of succeeding.

**Fix**: delegate to the repository instead of duplicating (and under-implementing) its logic:

```python
ClassroomRepository.delete(id=id, user=self.user, session=self.session)
self.session.commit()
```

This also incidentally picked up the `ClassroomPermission` cleanup from the previous fix, since it's implemented in the same repository method.

**Caught by**: `test_deletes_a_classroom_with_an_allocated_schedule`.

---

### `OccurrenceRepositoryAdapter.allocate_schedule` allocated schedules without checking `ALLOCATE` permission on the classroom

**Found while**: writing `tests/integration/deps/repository_adapters/test_occurrence_repository_adapter.py`.

**File**: `server/deps/repository_adapters/occurrence_repository_adapter.py`

**Bug**: the singular `allocate_schedule` method resolved its inputs via `self.schedule_repo.get_by_id(schedule_id)` and `self.classroom_repo.get_by_id(classroom_id)` and then allocated directly, with no explicit permission check of its own:

```python
def allocate_schedule(self, schedule_id: int, classroom_id: int, ...) -> Schedule:
    schedule = self.schedule_repo.get_by_id(schedule_id)
    classroom = self.classroom_repo.get_by_id(classroom_id)
    OccurrenceRepository.allocate_schedule(user=self.user, schedule=schedule, classroom=classroom, session=self.session)
    ...
```

`classroom_repo.get_by_id()` only enforces `ClassroomAction.READ`, not `ALLOCATE`. Its sibling method right below it, `allocate_schedule_many`, explicitly checks `ClassroomAction.ALLOCATE` on both the schedule and the classroom before allocating — this method didn't, so a user with a role-granted `READ` permission on a classroom (without `ALLOCATE`) could allocate schedules into it via this endpoint (`POST /occurrences/allocate-schedule`, also used internally by `PATCH /allocations/events`), bypassing the `ALLOCATE` grant entirely.

**Risk**: authorization bypass — a restricted user with only `READ` access to a classroom could reassign schedules into it, an action meant to be gated behind a separate, more privileged grant.

**Fix**: added the same explicit checks `allocate_schedule_many` already had:

```python
schedule = self.schedule_repo.get_by_id(schedule_id)
self.schedule_checker.check_permission(schedule, ClassroomAction.ALLOCATE)
classroom = self.classroom_repo.get_by_id(classroom_id)
self.checker.check_permission(classroom, ClassroomAction.ALLOCATE)
```

**Caught by**: `TestAllocateSchedule::test_denies_without_classroom_allocate_permission` (grants only `READ` on a classroom outside the user's group, asserts `ForbiddenClassroomAccess`) and `test_allocates_via_granted_permissions` (same setup plus `ALLOCATE`, asserts success).

---

### `HolidayCategoryRepository.create` / `HolidayRepository.create` / `CalendarRepository.create` leaked their unique-constraint violation as an unhandled 500

**Found while**: writing `tests/integration/repositories/test_holiday_category_repository.py`, `test_holiday_repository.py`, and `test_calendar_repository.py`.

**Files**: `server/repositories/holiday_category_repository.py`, `server/repositories/holiday_repository.py`, `server/repositories/calendar_repository.py`

**Bug**: all three `create` methods have a real DB unique constraint behind them — `HolidayCategory` on `(name, year)`, `Holiday` on `(date, category_id)`, `Calendar` on `(name, year)` — but none of the three caught the resulting `IntegrityError`, and none of their route handlers did either. Creating a duplicate crashed with a raw 500. The smoking gun: `holiday_repository.py` already defined a `HolidayInCategoryAlreadyExists` exception, clearly meant for exactly this case — but nothing ever raised it, so it sat as dead code.

**Risk**: this is the exact same class of bug as `BuildingRepositoryAdapter.create` (see above) — a completely routine "you already have one of these" user mistake surfaced as an opaque server error instead of a clean 409, across three different resources.

**Fix**: wrapped each `session.add(...)`/`session.commit()` in `try/except IntegrityError`, rolling back and raising a proper 409. Added `HolidayCategoryAlreadyExists` and `CalendarAlreadyExists` (mirroring the existing `HolidayInCategoryAlreadyExists`, now finally wired up):

```python
session.add(new_holiday)
try:
    session.commit()
except IntegrityError:
    session.rollback()
    raise HolidayInCategoryAlreadyExists(input.date.strftime("%d/%m/%Y"), category.name)
session.refresh(new_holiday)
```

**Caught by**: `test_raises_on_duplicate_name_and_year`/`test_raises_on_duplicate_date_in_the_same_category` in each of the three new test files.

---

### `HolidayCategoryRepository.get_by_name` raised a raw `NoResultFound` instead of `HolidayCategoryNotFound`

**Found while**: writing `tests/integration/repositories/test_holiday_category_repository.py`.

**File**: `server/repositories/holiday_category_repository.py`

**Bug**: unlike every sibling lookup in the same file (`get_by_id`, `get_by_ids`), `get_by_name` called `.one()` with no `try/except`:

```python
holiday_category = session.exec(statement).one()
```

An unknown name raised `sqlalchemy.exc.NoResultFound` directly instead of the domain `HolidayCategoryNotFound` every other lookup in this repository (and `CalendarRepository.get_by_name`, which correctly uses `.first()` + a `None` check) produces.

**Risk**: currently unused by any route, so latent rather than active — but the inconsistency is exactly the kind of thing that bites the first caller that reaches for it, expecting the same 404 contract as every other lookup in the file.

**Fix**: matched the `get_by_id` pattern:

```python
try:
    holiday_category = session.exec(statement).one()
except NoResultFound:
    raise HolidayCategoryNotFound(f"nome: {name}")
```

**Caught by**: `TestGetByName::test_raises_for_an_unknown_name`.

---

### `HolidayRepository.check_date_is_valid` compared a `datetime` against a `Date` column and could never match

**Found while**: writing `tests/integration/repositories/test_holiday_repository.py`.

**File**: `server/repositories/holiday_repository.py`

**Bug**: `Holiday.date` is a `Date` column, but the method compared it directly against its `date: datetime` parameter without truncating:

```python
.where(col(Holiday.date) == date)
```

A caller passing a real timestamp (e.g. `BrazilDatetime.now_utc()`, which is exactly what the parameter's own type hint implies is expected) would never match an existing holiday's stored date unless the timestamp happened to land on exactly midnight — the check silently reported "valid" (no conflict) even when a holiday already existed on that calendar day.

**Risk**: this method has no current callers, so it's latent rather than active — but it's a straightforward "is this date already taken" guard, and as written it can never actually say no.

**Fix**: truncate to the date part before comparing:

```python
.where(col(Holiday.date) == date.date())
```

**Caught by**: `TestCheckDateIsValid::test_returns_false_when_a_holiday_already_exists_on_the_date`, which failed against the original code (returned `True`/"valid" for a date that already had a holiday).

---

## Tested with no bugs found

- `RoleRepository` (`tests/integration/repositories/test_role_repository.py`) — `create`, `update`, `delete`, `get_by_id`, `get_all` (with/without a resource filter) all behaved as documented, including permission deduplication and the current-vs-desired permission diffing in `update`.
- `UserScheduleRepository` (`tests/integration/repositories/test_user_schedule_repository.py`) — `get_by_id`, `get_active_current_schedule`, `invalidate_expired_current_schedules`, `update_from_schedules`, `create_from_schedules`, and `delete` all behaved as documented. Specifically verified: inactive schedules are rejected, `start_date`/`end_date` are derived as the min/max across the given schedules, repeated schedules are deduplicated into a single entry, an entry for a schedule that stays across an update is *reused* (its `absence_count` is preserved) rather than recreated, and deleting a `UserSchedule` cascades to its `UserScheduleEntry` rows via the model's `cascade="all, delete-orphan"` relationship (the commented-out manual entry-deletion loop in `UserScheduleRepository.delete` is dead code, not a missing safeguard — the ORM cascade already handles it).
- `EventRepository` / `MeetingRepository` (`test_event_repository.py`, `test_meeting_repository.py`) — `create` (with `allocate=True`/`False`), `get_by_id`, `get_all` interval filtering, and `update` (including reallocating to a different classroom) all matched their documented behavior.
- `ExamRepository` (`test_exam_repository.py`) — `create`/`update` correctly reject a class that belongs to a different subject than the exam (`ExamInvalidClassAndSubject`); `get_all_by_subject_id`/`get_all_by_class_id` scope correctly.
- `ReservationRepository` (`test_reservation_repository.py`) — beyond the two bugs above: `create`, `get_all`/`get_all_on_buildings`/`get_all_on_classrooms` interval and scope filtering, `update` (including reallocation on classroom change), and `delete` (hard-delete when there's no solicitation; soft-delete via the solicitation's status when there is one, correctly rejecting a second delete of an already-deleted one) all matched their documented behavior.
- `SolicitationRepository` (`test_solicitation_repository.py`, 29 tests) — the full lifecycle held up under test: building/classroom-mismatch and non-reservable-classroom validation on both `create` and `update`; owner-only `update` with a `SolicitationAlreadyClosed` guard once no longer pending and a rejection on changing reservation type; `approve` correctly enforces `required_classroom` against the solicited classroom while still allowing a different one when it isn't required, and validates the approved classroom's building; `deny` and `cancel`'s permission/status rules (note: `cancel`, unlike `approve`/`deny`, has no "already closed" guard — appears intentional, since cancelling something already approved/denied is a plausible action, not re-flagged as a bug here).
- `ClassRepositoryAdapter`, `EventRepositoryAdapter`, `ExamRepositoryAdapter`, `MeetingRepositoryAdapter`, `ReservationRespositoryAdapter`, `ScheduleRepositoryAdapter`, `SubjectRepositoryAdapter` (`tests/integration/deps/repository_adapters/`) — permission gating (deny/allow via role grants), duplicate-name/code conflicts, and cross-resource validation (e.g. `ClassroomInsertionOnInvalidGroup`, `InvalidScheduleInput`) all matched their documented behavior. Note: `EventModelFactory`/`MeetingModelFactory`/`ExamModelFactory` (via `ReservationModelFactory`) never actually wire the `classroom` they're given onto the created schedule — a pre-existing, already-documented test-factory quirk (see the comment/workaround already in `tests/api/public/test_event_routes.py` et al.), not a production bug; reservation-adapter tests reuse the same `schedule.classroom = classroom` workaround.
