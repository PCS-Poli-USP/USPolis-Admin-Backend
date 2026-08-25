# Permissions

How the role-based permission system works: the data model, the one-time
migration from the older `Group` model, and how a request gets from a route
dependency to an allow/deny decision.

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
— `CREATE`, `READ`, `UPDATE`, `DELETE`, and for `BUILDING`/`CLASSROOM` also
`ALLOCATE`/`RESERVE`) to a resource (`Resource.BUILDING` / `CLASSROOM` /
`COURSE`, `server/utils/enums/resources_enums.py`), either a specific
instance (`resource_id`) or a wildcard (`resource_id = -1` in requests,
stored as `NULL`) meaning "every instance of that resource".

- A `BuildingPermission` cascades down to every `Classroom` inside that
  building for the same action, so granting e.g. `ALLOCATE` on a building
  lets a role allocate any room in it without needing one
  `ClassroomPermission` per room.
- A wildcard grant (no specific building/classroom/course) is only honored
  for `UPDATE`, `DELETE`, `ALLOCATE`, and `RESERVE` when the requesting user
  is an admin (`GLOBAL_WILDCARD_ADMIN_ONLY_ACTIONS` in
  `server/services/security/role_permission_evaluator.py`) — a non-admin
  role can never be granted "update/delete/allocate/reserve everything in
  the system at once" through a wildcard permission, only through a
  building- or resource-scoped one. `CREATE`/`READ` wildcards are honored
  for any role.
- `Resource.COURSE` / `CoursePermission` exist in the data model but have no
  wired permission checker yet — no route enforces them today.

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
| Create a classroom | `BUILDING` | `CREATE` | Checked on the classroom's building |
| Read a classroom | `CLASSROOM` | `READ` | |
| Update a classroom | `CLASSROOM` | `UPDATE` | |
| Delete a classroom | `CLASSROOM` | `DELETE` | Wildcard grant is admin-only |
| Allocate/reallocate a classroom to a class's weekly schedule | `CLASSROOM` | `ALLOCATE` | Also requires `UPDATE` on the `Class` that owns the `Schedule` |
| Create/update/cancel a `Reservation`, `Meeting`, `Event`, or `Exam` | `CLASSROOM` (or `BUILDING` if the booking has no classroom yet) | `RESERVE` | Covers the entire booking lifecycle, including deletion |
| Approve/deny a `Solicitation` | `CLASSROOM` | `RESERVE` | Approving/denying is fundamentally creating-or-refusing a `Reservation` |
| Create a subject ("disciplina") | `BUILDING` | `CREATE` | |
| Read a subject | `BUILDING` | `READ` | |
| Update a subject | `BUILDING` | `UPDATE` | |
| Delete a subject | `BUILDING` | `UPDATE` | Not `DELETE` — see rule 2 above |
| Create a class ("turma") | `BUILDING` | `CREATE` | Checked via the class's subject/building |
| Read a class | `CLASSROOM` | `READ` | |
| Update a class | `CLASSROOM` | `UPDATE` | |
| Delete a class | `CLASSROOM` | `UPDATE` | Not `DELETE` — see rule 2 above |

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
Retiring `Group` entirely — dropping its tables/columns and the `OR`
fallback, leaving `Role`/`Permission` as the sole source of truth — is a
later, separate step (tracked as its own phase, not yet started).
