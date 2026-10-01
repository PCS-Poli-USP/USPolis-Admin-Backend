from collections.abc import Sequence

from sqlmodel import Session

from server.models.database.role_db_model import Role
from server.models.database.user_db_model import User
from server.models.database.user_role_db_model import UserRole
from server.repositories.building_permission_repository import (
    BuildingPermissionRepository,
)
from server.repositories.classroom_permission_repository import (
    ClassroomPermissionRepository,
)
from server.utils.enums.actions_enums import (
    BuildingAction,
    ClassroomAction,
    PermissionAction,
)
from server.utils.enums.resources_enums import Resource
from server.utils.must_be_int import must_be_int
from tests.factories.model.role_model_factory import RoleModelFactory
from tests.factories.request.permission_request_factory import (
    PermissionRequestFactory,
)


class RolePermissionTestHelper:
    """Shared setup for tests that need a user to hold a Role-granted
    permission. A permission can only ever be granted to a Role, never
    directly to a user (see PERMISSIONS.md) - so every such test needs the
    same three steps: create a role, grant it a permission as some granting
    admin, then assign that role to the target user. `grant_by` is the
    actor recorded as having granted the permission/role (normally an admin)
    and is always distinct from `user`, the recipient.
    """

    @staticmethod
    def assign_role(
        *, user: User, role: Role, granted_by: User, session: Session
    ) -> None:
        session.add(
            UserRole(
                user_id=must_be_int(user.id),
                role_id=must_be_int(role.id),
                granted_by_id=must_be_int(granted_by.id),
            )
        )
        session.commit()
        session.refresh(user)

    @staticmethod
    def grant_building_permission(
        *,
        user: User,
        resource_id: int,
        actions: Sequence[BuildingAction],
        granted_by: User,
        session: Session,
    ) -> Role:
        """Create a Role scoped to BUILDING, grant it a BuildingPermission for
        `resource_id` (pass -1 for a wildcard grant), and assign the role to
        `user`. Returns the created role."""
        role = RoleModelFactory(
            session=session, resources=[Resource.BUILDING]
        ).create_and_refresh()
        actions_list: list[PermissionAction] = list(actions)
        permission_input = PermissionRequestFactory(
            role=role, resource=Resource.BUILDING
        ).create_input(resource_id=resource_id, actions=actions_list)
        BuildingPermissionRepository.create(
            input=permission_input, user=granted_by, session=session
        )
        RolePermissionTestHelper.assign_role(
            user=user, role=role, granted_by=granted_by, session=session
        )
        return role

    @staticmethod
    def grant_classroom_permission(
        *,
        user: User,
        resource_id: int,
        actions: Sequence[ClassroomAction],
        granted_by: User,
        session: Session,
    ) -> Role:
        """Create a Role scoped to CLASSROOM, grant it a ClassroomPermission
        for `resource_id` (pass -1 for a wildcard grant), and assign the role
        to `user`. Returns the created role."""
        role = RoleModelFactory(
            session=session, resources=[Resource.CLASSROOM]
        ).create_and_refresh()
        actions_list: list[PermissionAction] = list(actions)
        permission_input = PermissionRequestFactory(
            role=role, resource=Resource.CLASSROOM
        ).create_input(resource_id=resource_id, actions=actions_list)
        ClassroomPermissionRepository.create(
            input=permission_input, user=granted_by, session=session
        )
        RolePermissionTestHelper.assign_role(
            user=user, role=role, granted_by=granted_by, session=session
        )
        return role
