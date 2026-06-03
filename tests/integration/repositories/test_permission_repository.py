from sqlmodel import Session

from server.models.database.role_db_model import Role
from server.models.database.user_db_model import User
from server.repositories.building_permission_repository import (
    BuildingPermissionRepository,
)
from server.utils.enums.actions_enums import BuildingAction
from server.utils.enums.resources_enums import Resource
from server.models.http.requests.permission_request_models import PermissionRegister


def test_permission_repository_create_adds_resource_to_role(
    user: User, session: Session
) -> None:
    role = Role(name="Test Role", description="", resources=[Resource.CLASSROOM])
    session.add(role)
    session.commit()
    session.refresh(role)

    permission_input = PermissionRegister(
        resource=Resource.BUILDING,
        resource_id=-1,
        actions=[BuildingAction.CREATE],
        role_id=role.id,
    )

    BuildingPermissionRepository.create(
        input=permission_input,
        user=user,
        session=session,
    )
    session.commit()
    session.refresh(role)

    assert Resource.CLASSROOM in role.resources
    assert Resource.BUILDING in role.resources
