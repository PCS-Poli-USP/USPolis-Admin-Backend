from collections import defaultdict
from dataclasses import dataclass

from server.models.database.building_permission_db_model import BuildingPermission
from server.models.database.classroom_permission_db_model import ClassroomPermission
from server.models.database.course_permission_db_model import CoursePermission
from server.models.database.user_db_model import User
from server.utils.enums.actions_enums import BaseAction, ClassroomAction, PermissionAction
from server.utils.enums.resources_enums import Resource
from server.utils.permissions_types import Permission

# A global wildcard grant (no specific building/classroom/course) is only honored
# for these actions when the user is a real admin: a non-admin role can never be
# granted "update/delete/allocate/reserve everything in the system" through a
# wildcard permission, only through a building- or resource-scoped one.
GLOBAL_WILDCARD_ADMIN_ONLY_ACTIONS = frozenset(
    {BaseAction.UPDATE, BaseAction.DELETE, ClassroomAction.ALLOCATE, ClassroomAction.RESERVE}
)

_EMPTY_IDS: frozenset[int] = frozenset()

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
        return key in self._wildcard and action not in GLOBAL_WILDCARD_ADMIN_ONLY_ACTIONS

    def has_classroom_permission(
        self, *, action: ClassroomAction, classroom_id: int | None, building_id: int | None
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
                key = (resource, action)
                if target_id is None:
                    wildcard.add(key)
                else:
                    exact[key].add(target_id)

    return PermissionIndex(
        is_admin=user.is_admin,
        _exact={key: frozenset(ids) for key, ids in exact.items()},
        _wildcard=frozenset(wildcard),
    )
