# Permissions

How the role-based permission system works: the data model, the one-time
migration from the older `Group` model, and how a request gets from a route
dependency to an allow/deny decision.

The developer reference at https://www.uspolis.com.br/docs/dev/backend/permissions
(pt-BR, source in the frontend repo at `docs/dev/backend/permissions.md`)
explains every rule with examples. This file is the backend-side summary; keep
both in sync, and add a test in `tests/api/roles/` (a user with roles only, no
group) for every rule.

## The model

A `Role` (`server/models/database/role_db_model.py`) groups a set of
`Permission`s and is assigned to `User`s via `/admin/roles`. A permission is
always granted to a role — there is no way to grant a permission directly to
a single user ("point permissions") anymore, every permission row requires a
`role_id` (`server/models/database/base_permission_db_model.py`).

Three concrete permission tables extend the shared `BasePermission`
(`role_id`, `granted_at`, `granted_by_id`):

- `BuildingPermission` (`server/models/database/building_permission_db_model.py`)
- `ClassroomPermission` (`server/models/database/classroom_permission_db_model.py`)
- `CoursePermission` (`server/models/database/course_permission_db_model.py`)

Each permission scopes a set of `action`s (`server/utils/enums/actions_enums.py`
— `CREATE`, `READ`, `UPDATE`, `DELETE`, for `BUILDING`/`CLASSROOM` also
`ALLOCATE`/`RESERVE`, and for `CLASSROOM` also `REQUEST`) to a resource (`Resource.BUILDING` / `CLASSROOM` /
`COURSE`, `server/utils/enums/resources_enums.py`), either a specific
instance (`resource_id`) or a wildcard (`resource_id = -1` in requests,
stored as `NULL`) meaning "every instance of that resource".

- A `BuildingPermission` cascades down to every `Classroom` inside that
  building for the same action, so granting e.g. `ALLOCATE` on a building
  lets a role allocate any room in it without needing one
  `ClassroomPermission` per room.
- A wildcard grant (no specific building/classroom/course) is only honored
  for `UPDATE`, `DELETE`, `ALLOCATE`, `RESERVE`, and `REQUEST` when the requesting user
  is an admin (`GLOBAL_WILDCARD_ADMIN_ONLY_ACTIONS` in
  `server/services/security/role_permission_evaluator.py`) — a non-admin
  role can never be granted "update/delete/allocate/reserve everything in
  the system at once" through a wildcard permission, only through a
  building- or resource-scoped one. `CREATE`/`READ` wildcards are honored
  for any role.
- `Resource.COURSE` / `CoursePermission` exist in the data model but have no
  wired permission checker yet — no route enforces them today.

### Implied actions

Some actions make no sense alone, so granting one grants what it depends on
(`IMPLIED_ACTIONS`, applied by `build_permission_index`, so existing roles
follow it with no data migration):

| Granted | Also grants, on the same resource |
|---|---|
| `CREATE`, `UPDATE`, `ALLOCATE`, `RESERVE`, `REQUEST` | `READ` |
| `DELETE` | `UPDATE`, `READ` |

Nothing else is implied (`UPDATE` does not imply `ALLOCATE` or `DELETE`). A
wildcard for an admin-only action is ignored for non-admins, and so is the
`READ`-on-everything it would imply.

### Belonging to a building, and the access scope

A user **belongs to a building** when they can read it, or read at least one
classroom in it (role, group or cascade). That gives visibility (the building
in filters, the classes of its subjects), not actions.

`AccessScope` (`server/services/security/access_scope.py`, injected as
`AccessScopeDep`, one per request) resolves per action the buildings and
classrooms a user can act on: `building_grant`, `classroom_grant` (direct
grants, cascade from buildings, legacy groups) and `visible_building_grant`
(the action on the building or on any of its classrooms);
`readable_building_ids()` is the buildings the user belongs to. Every listing
scopes with it (`READ`; the solicitation inbox uses `RESERVE`), and
`GET /users/my-access` returns it already resolved for the frontend. Legacy
groups are added only in its `_legacy_group_*` methods.

### Class and subject visibility

A class has no building of its own: its subject is linked to one or more
buildings. Whoever belongs to one of the subject's buildings **reads every
class of that subject**, allocated or not, wherever its schedules are (e.g.
Calculus I is offered in several buildings, and a class can have one schedule
in each). Everything else (`UPDATE`, ...) goes through the schedules: the
action on the classroom of an allocated schedule, or on one of the subject's
buildings for an unallocated one (`ClassPermissionChecker`). Subjects follow
the same read rule (`SubjectPermissionChecker`). Deleting a class takes
`UPDATE` on the class and on **every** schedule.

### Allocation

`OccurrenceRepositoryAdapter.check_can_allocate`, used by every allocation
path (`allocate-schedule`, `allocate-schedule-many`,
`remove-schedule-allocation`, `PATCH /allocations/events`,
`allocate-allocation-map`):

1. `ALLOCATE` on the target classroom and, when the schedule or occurrence is
   already allocated, on the classroom it leaves. Deallocating takes
   `ALLOCATE` on the current classroom.
2. Nothing on the class or its building: a classroom-level role allocates in
   its own classrooms.
3. A class only goes into classrooms of its subject's buildings — 400 for
   everyone, admins included, since the class would otherwise be invisible
   to that building's users. Add the subject to the building first.

Manage roles and permissions via `/admin/roles`
(`server/routes/admin/roles_admin_routes.py`: `GET`/`POST`/`PUT`/`DELETE`
`/admin/roles`, `GET /admin/roles/{role_id}`) and `/admin/permissions`
(`server/routes/admin/permissions_admin_routes.py`: `GET`/`POST`/`PUT`/
`DELETE /admin/permissions`, `GET /admin/permissions/all`,
`POST /admin/permissions/batch`).

## What action do I need? (action → operation mapping)

Every write/read endpoint resolves to one `(Resource, Action)` pair checked
against the requesting user's roles (and, for now, `Group` membership as a
fallback — see below). Two design rules keep this mapping predictable:

1. **`DELETE` is reserved for destroying the record itself** (a `Building`,
   a `Classroom`, a `Subject`, a `Class`) — never reused for a lesser, more
   common operation, since granting `DELETE` on a resource is a
   comparatively severe grant (and, for `BUILDING`/`CLASSROOM`, a wildcard
   `DELETE` grant is admin-only, see above).
2. **Deleting/canceling a `Reservation` (and everything built on top of it —
   `Meeting`, `Event`, `Exam`, `Solicitation` approve/deny) is `RESERVE`, not
   `DELETE`**, since booking and un-booking a room is a routine, everyday
   action that shouldn't require (or imply) the ability to delete the room
   itself. For the same reason, **deleting a `Class` ("turma") or a
   `Subject` ("disciplina") is gated by `UPDATE`, not `DELETE`** — a user
   who can manage the academic offering in a building shouldn't thereby
   also be granted the ability to delete the physical `Building`/`Classroom`
   record, which is a much more impactful action.

| I want to... | Resource checked | Action required | Notes |
|---|---|---|---|
| Create a building | `BUILDING` | `CREATE` | No instance yet ("creation" check); only admins hit this route today |
| Read a building | `BUILDING` | `READ` | |
| Update a building | `BUILDING` | `UPDATE` | |
| Delete a building | `BUILDING` | `DELETE` | Wildcard grant is admin-only |
| Create a classroom | `BUILDING` | `CREATE` | Checked on the classroom's building. Groups are optional (`group_ids` may be empty) |
| Read a classroom | `CLASSROOM` | `READ` | |
| Update a classroom | `CLASSROOM` | `UPDATE` | |
| Delete a classroom | `CLASSROOM` | `DELETE` | Wildcard grant is admin-only |
| Allocate, reallocate or deallocate a schedule (or a single occurrence) | `CLASSROOM` | `ALLOCATE` | On the classroom it leaves **and** on the one it goes to; nothing on the `Class` or its building. A class only goes into classrooms of its subject's buildings (400, admins included). See [Allocation](#allocation) |
| Create/update/cancel a `Reservation`, `Meeting`, `Event`, or `Exam` | `CLASSROOM` (or `BUILDING` if the booking has no classroom yet) | `RESERVE` | Covers the entire booking lifecycle, including deletion |
| Approve/deny a `Solicitation` | `CLASSROOM` | `RESERVE` | Approving/denying is fundamentally creating-or-refusing a `Reservation` |
| Create/update a `Solicitation` targeting a `restricted` classroom | `CLASSROOM` | `REQUEST` | Only checked when the targeted classroom has `restricted=True`; unrestricted classrooms or solicitations with no classroom chosen yet need no check here |
| Create a subject ("disciplina") | `BUILDING` | `CREATE` | |
| Read a subject | `BUILDING` | belong to one of its buildings | See [Class and subject visibility](#class-and-subject-visibility) |
| Update a subject | `BUILDING` | `UPDATE` | |
| Delete a subject | `BUILDING` | `UPDATE` | Not `DELETE` — see rule 2 above (a `DELETE` grant implies `UPDATE`, so it also deletes subjects) |
| Create a class ("turma") | `BUILDING` | `CREATE` | Checked via the class's subject/building |
| Read a class | — | belong to one of its subject's buildings, or read the classroom of one of its schedules | See [Class and subject visibility](#class-and-subject-visibility) |
| Update a class | `CLASSROOM` | `UPDATE` | On the classroom of an allocated schedule, or `BUILDING` `UPDATE` for an unallocated one |
| Delete a class | `CLASSROOM` | `UPDATE` | Not `DELETE` — see rule 2 above. On the class and on every schedule |
| Re-crawl subjects (`PATCH /subjects/crawl`) | `BUILDING` | `UPDATE` | On **every** subject asked for; one of another building refuses the whole request |
| Create schedules for a class, edit a schedule's occurrences | `CLASSROOM` | `UPDATE` | As updating the class; a new schedule that comes with a classroom also takes `ALLOCATE` on it |
| Allocation reuse options | — | `READ` on every class asked for | |
| Conflict count per classroom (`/classrooms/with-conflict-count`, `GET` and `POST`) | `BUILDING` | belong to the building | Lists only the classrooms the user can read |
| Users of a building (`GET /users/{building_id}`) | `BUILDING` | belong to the building | Returns id, name and email only |

### Owner routes, global entities and the mobile app

- **User schedules** (`/users/schedules`): only their owner edits or deletes
  one, admins included (personal data).
- **Solicitations**: only the requester edits one (admins included); the
  requester or an admin cancels it.
- **Holiday categories, holidays, calendars, institutional events**: any
  user of the `restricted` tier creates one; only its creator or an admin
  edits or deletes it. `InstitutionalEvent.created_by_id` (migration
  `5c2e8a7f9d14`) is NULL for events created before it, which only admins
  change. A like from the app is not an edit (`save_likes`).
- **Solicitation emails** (new and cancelled): sent to whoever can approve
  it, with emails on (`server/services/security/solicitation_recipients.py`):
  RESERVE on its classroom (directly or through the building), or, with no
  classroom, RESERVE on its building or any classroom of it (the inbox rule);
  plus the matching legacy group members. Admins only through a role or a
  group; a RESERVE wildcard does not count (ignored).
- **Mobile app writes** (`/mobile/*`: post, reply, like, report, "Fale
  conosco"): the app user comes from the Google ID token in `Authorization`
  (`MobileUserDep`, `server/deps/google_auth_dep.py`), never from the body;
  a body `user_id` must match it (`check_acting_as`, 403). Deleting a post is
  for its author only; listing the "Fale conosco" messages
  (`GET /mobile/comments`) is admin-only.

## How the rules are tested

Every route has a class in `tests/api/roles/route_registry.py`
(`ROUTE_REGISTRY`: `PUBLIC`, `HEALTH`, `MOBILE`, `SELF`, `GLOBAL_READ`,
`RESTRICTED_ANY`, `OWNER`, `OBJECT(resource, action)`, `ADMIN`; everything
under `/admin` is `ADMIN` by prefix). Table-driven suites in
`tests/api/roles/`, as a user with roles only:

| File | Checks |
|---|---|
| `test_route_guard.py` | the registry matches `app.routes`; each route's authentication matches its class (read from its dependency tree); 401 without credentials, 403 at the restricted gate, 403 on admin routes even for the broadest role |
| `test_permission_matrix.py` | every `OBJECT` route under up to seven variants: exact grant, none, other building, read only, building cascade, wildcard, legacy group |
| `test_listings.py` | every listing, an object of building A against one of building B |
| `test_owner_routes.py` | every `OWNER` route as the owner, another user and an admin |
| `test_implications.py` | every pair of `IMPLIED_ACTIONS`, plus what is not implied |

**A new route fails the suite until it is classified**: add its line to
`ROUTE_REGISTRY` and, by class, to the matrix (`OPERATIONS`), listing
(`LISTINGS`) or owner (`OWNER_OPERATIONS`) table; each table has a coverage
test naming the missing line. The variants of each table are spelled out in
the developer reference (section "Como cada rota é classificada").

## `PermissionIndex`: how a check actually resolves

Building the index — `server/services/security/role_permission_evaluator.py`:

- `build_permission_index(user: User) -> PermissionIndex` walks every role
  and permission the user has **once**, flattening them into two lookup
  structures: `_exact` (a `(Resource, Action) -> set[resource_id]` map) and
  `_wildcard` (a `set[(Resource, Action)]` of resource-wide grants).
- The resulting `PermissionIndex` is a frozen dataclass with two query
  methods: `has_permission(resource, action, resource_id)` (exact-id-or-
  wildcard check, admin always `True`) and `has_classroom_permission(action,
  classroom_id, building_id)` (checks a direct `ClassroomPermission` first,
  then falls back to the cascading `BuildingPermission` for that classroom's
  building).
- The doctring on `PermissionIndex` is explicit about why it's built once
  and reused: rebuilding it walks every role/permission the user has, so
  doing that per individual check defeats the point of the O(1) lookup.

Wiring it into a request — `server/deps/permission_index_dep.py`:

```python
def permission_index(user: UserDep) -> PermissionIndex:
    return build_permission_index(user)

PermissionIndexDep = Annotated[PermissionIndex, Depends(permission_index)]
```

`PermissionIndexDep` is built **once per request** (standard FastAPI
dependency caching within a request) and injected wherever a permission
decision is needed — either directly into a route handler, or (the more
common pattern) into a repository adapter's `__init__`
(`server/deps/repository_adapters/*.py`), which then constructs one or more
`*PermissionChecker`s from it once and reuses them across all the methods on
that adapter for the lifetime of the request:

```python
class EventRepositoryAdapter:
    def __init__(
        self, user: UserDep, session: SessionDep, permission_index: PermissionIndexDep
    ):
        self.checker = ReservationPermissionChecker(
            user=user, session=session, permission_index=permission_index
        )
        self.classroom_checker = ClassroomPermissionChecker(
            user=user, session=session, permission_index=permission_index
        )

    def create(self, creator: User, input: EventRegister) -> Event:
        ...
        self.classroom_checker.check_permission(classroom, ClassroomAction.RESERVE)
```

The checker layer (`server/services/security/*_permission_checker.py`) all
share the same shape: subclass `PermissionChecker`
(`base_permission_checker.py`), accept an object (an id, a model instance,
or a list of either) plus an `action`, short-circuit `True` for
`user.is_admin`, and otherwise delegate to the `PermissionIndex`. On denial
they raise a resource-specific `HTTPException` subclass (403) — e.g.
`ClassroomPermissionChecker` raises `ForbiddenClassroomAccess`. Some
checkers compose others: `ReservationPermissionChecker` wraps both a
`ClassroomPermissionChecker` and a `BuildingPermissionChecker` internally,
since a reservation's access is determined by whichever of the two the
underlying booking actually has.

## The `Group` → `Role` migration and the current dual-check state

> [!WARNING]
> Request-time authorization on every resource endpoint currently checks
> **both** `Group` membership (legacy) **and** `Role`/`Permission`
> (`user has access OR role grants access`), so existing `Group`-based
> access keeps working unchanged while `Role` grants are additive.

Every pre-existing `Group` was migrated into an equivalent `Role` by
`migrations/versions/6950bd048a6d_migrate_group_data_into_role_permission_.py`,
so both models currently describe the same access for existing users:

1. For each `Building`, create a `Role` for the building's main `Group` and
   grant it `BuildingPermission` (`CREATE`/`READ`/`UPDATE`/`ALLOCATE`/
   `RESERVE`) on that building.
2. For each non-main `Group` in the building, create a `Role` and grant it
   `ClassroomPermission` on every classroom that group had.
3. For each user in a migrated group, grant them the corresponding role via
   `UserRole`.

The migration is a no-op on a database with no `Building` rows yet (it
returns immediately rather than requiring an admin user to attribute the
grants to), and its `downgrade()` removes every role/permission it created
by matching on a `"Migrado automaticamente"` description marker rather than
tracking ids separately.

The `is_allowed`-style check in each checker (e.g.
`ClassroomPermissionChecker.is_allowed`) shows the fallback order directly:
the legacy `Group`-based check (`user.classrooms_ids_set()`) runs first,
and only if that's `False` does it fall through to the `PermissionIndex`.
The tier gate in front of all of this accepts both models:
`restricted_authenticate` (`server/deps/authenticate.py`) lets a request
into the `restricted` tier if the user is an admin, has at least one
`Group`, or has at least one `Role`. The gate only decides who enters the
tier; what a role-only user can touch inside it is still decided per object
by the checkers above. The frontend mirrors the gate in `hasRestrictedAccess`
(`src/utils/users/users.formatter.ts`: admin, a building, or a role), which
is why `UserResponse` (`GET /users`) carries `role_ids`. Change both sides
together.

Retiring `Group` entirely — dropping its tables/columns and the `OR`
fallback, leaving `Role`/`Permission` as the sole source of truth — is a
later, separate step (tracked as its own phase, not yet started).
