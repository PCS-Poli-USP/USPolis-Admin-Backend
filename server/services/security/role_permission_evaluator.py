from collections import defaultdict
from dataclasses import dataclass

from server.models.database.building_permission_db_model import BuildingPermission
from server.models.database.classroom_permission_db_model import ClassroomPermission
from server.models.database.course_permission_db_model import CoursePermission
from server.models.database.user_db_model import User
from server.utils.enums.actions_enums import (
    BaseAction,
    ClassroomAction,
    PermissionAction,
)
from server.utils.enums.resources_enums import Resource
from server.utils.permissions_types import Permission

# A global wildcard grant (no specific building/classroom/course) is only honored
# for these actions when the user is a real admin: a non-admin role can never be
# granted "update/delete/allocate/reserve/request everything in the system" through
# a wildcard permission, only through a building- or resource-scoped one.
GLOBAL_WILDCARD_ADMIN_ONLY_ACTIONS = frozenset(
    {
        BaseAction.UPDATE,
        BaseAction.DELETE,
        ClassroomAction.ALLOCATE,
        ClassroomAction.RESERVE,
        ClassroomAction.REQUEST,
    }
)

_EMPTY_IDS: frozenset[int] = frozenset()

# Actions that make no sense alone grant the actions they depend on, so a role
# can never hold an inconsistent set (e.g. reserving a classroom it cannot read):
# - every action implies READ on the same resource;
# - DELETE also implies UPDATE (deleting something you cannot edit makes no
#   sense).
# Applied when the index is built, so existing roles follow it too.
IMPLIED_ACTIONS: dict[str, frozenset[str]] = {
    BaseAction.CREATE: frozenset({BaseAction.READ}),
    BaseAction.UPDATE: frozenset({BaseAction.READ}),
    BaseAction.DELETE: frozenset({BaseAction.UPDATE, BaseAction.READ}),
    ClassroomAction.ALLOCATE: frozenset({BaseAction.READ}),
    ClassroomAction.RESERVE: frozenset({BaseAction.READ}),
    ClassroomAction.REQUEST: frozenset({BaseAction.READ}),
}


def with_implied_actions(
    actions: "list[PermissionAction] | frozenset[PermissionAction]",
) -> frozenset[str]:
    """`actions` plus every action they imply (see IMPLIED_ACTIONS)."""
    granted: set[str] = set(actions)
    for action in actions:
        granted |= IMPLIED_ACTIONS.get(action, frozenset())
    return frozenset(granted)


_PermissionKey = tuple[Resource, PermissionAction]


def _permission_target_id(permission: Permission) -> int | None:
    """Resource-specific id a permission grant targets, or None for a global wildcard."""
    if isinstance(permission, BuildingPermission):
        return permission.building_id
    if isinstance(permission, ClassroomPermission):
        return permission.classroom_id
    if isinstance(permission, CoursePermission):
        return permission.course_id
    return None


@dataclass(frozen=True, slots=True)
class PermissionIndex:
    """O(1) permission lookup for a single user, built once via `build_permission_index`.

    Build it once (e.g. once per request, as a cached dependency) and reuse it for
    every `has_permission`/`has_classroom_permission` call in that scope — each call
    is a couple of hash lookups, but rebuilding the index itself walks every role and
    permission the user has, so doing that per check defeats the point.
    """

    is_admin: bool
    _exact: dict[_PermissionKey, frozenset[int]]
    _wildcard: frozenset[_PermissionKey]

    def has_permission(
        self, *, resource: Resource, action: PermissionAction, resource_id: int | None
    ) -> bool:
        """Whether this user can perform `action` on `resource`, either for the exact
        `resource_id` given or via a global wildcard grant."""
        if self.is_admin:
            return True

        key = (resource, action)
        if resource_id is not None and resource_id in self._exact.get(key, _EMPTY_IDS):
            return True
        return (
            key in self._wildcard and action not in GLOBAL_WILDCARD_ADMIN_ONLY_ACTIONS
        )

    def ids_with_permission(
        self, *, resource: Resource, action: PermissionAction
    ) -> frozenset[int] | None:
        """The ids of `resource` this user can perform `action` on, through roles.

        None means every id: the user is an admin, or holds a wildcard grant
        that is honored for `action` (see GLOBAL_WILDCARD_ADMIN_ONLY_ACTIONS).
        Same rule as `has_permission`, for listing instead of checking one id.
        """
        if self.is_admin:
            return None
        key = (resource, action)
        if key in self._wildcard and action not in GLOBAL_WILDCARD_ADMIN_ONLY_ACTIONS:
            return None
        return self._exact.get(key, _EMPTY_IDS)

    def has_classroom_permission(
        self,
        *,
        action: ClassroomAction,
        classroom_id: int | None,
        building_id: int | None,
    ) -> bool:
        """Whether this user can perform `action` on a classroom, either through a
        direct ClassroomPermission or a cascading BuildingPermission for its building."""
        if self.has_permission(
            resource=Resource.CLASSROOM, action=action, resource_id=classroom_id
        ):
            return True
        if building_id is None:
            return False
        return self.has_permission(
            resource=Resource.BUILDING, action=action, resource_id=building_id
        )


def build_permission_index(user: User) -> PermissionIndex:
    """Walk every role/permission `user` has once and build an O(1)-lookup index."""
    exact: dict[_PermissionKey, set[int]] = defaultdict(set)
    wildcard: set[_PermissionKey] = set()

    for resource, permissions in user.get_user_permissions_map().items():
        for permission in permissions:
            target_id = _permission_target_id(permission)
            for action in permission.actions:
                if target_id is None:
                    wildcard.add((resource, action))
                    # A wildcard that is not honored (admin-only action, see
                    # has_permission) must not grant its implied actions on
                    # everything either.
                    if action in GLOBAL_WILDCARD_ADMIN_ONLY_ACTIONS:
                        continue
                    for implied in with_implied_actions([action]):
                        wildcard.add((resource, implied))  # type: ignore[arg-type]
                else:
                    for implied in with_implied_actions([action]):
                        exact[(resource, implied)].add(target_id)  # type: ignore[index]

    return PermissionIndex(
        is_admin=user.is_admin,
        _exact={key: frozenset(ids) for key, ids in exact.items()},
        _wildcard=frozenset(wildcard),
    )
