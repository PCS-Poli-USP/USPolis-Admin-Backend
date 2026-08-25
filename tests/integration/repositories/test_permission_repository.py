import pytest
from fastapi import HTTPException
from sqlmodel import Session

from server.models.database.role_db_model import Role
from server.models.database.user_db_model import User
from server.repositories.building_permission_repository import (
    BuildingPermissionRepository,
)
from server.utils.enums.actions_enums import BuildingAction
from server.utils.enums.resources_enums import Resource
from server.models.http.requests.permission_request_models import (
    PermissionRegister,
    PermissionUpdate,
)
from server.utils.must_be_int import must_be_int


def test_permission_repository_create_adds_resource_to_role(
    admin_user: User, session: Session
) -> None:
    role = Role(name="Test Role", description="", resources=[Resource.CLASSROOM])
    session.add(role)
    session.commit()
    session.refresh(role)

    permission_input = PermissionRegister(
        resource=Resource.BUILDING,
        resource_id=-1,
        actions=[BuildingAction.CREATE],
        role_id=must_be_int(role.id),
    )

    BuildingPermissionRepository.create(
        input=permission_input,
        user=admin_user,
        session=session,
    )
    session.commit()
    session.refresh(role)

    assert Resource.CLASSROOM in role.resources
    assert Resource.BUILDING in role.resources


def test_permission_repository_get_all_by_role_id(
    admin_user: User, role: Role, session: Session
) -> None:
    permission_input = PermissionRegister(
        resource=Resource.BUILDING,
        resource_id=-1,
        actions=[BuildingAction.CREATE],
        role_id=must_be_int(role.id),
    )
    BuildingPermissionRepository.create(input=permission_input, user=admin_user, session=session)
    session.commit()

    permissions = BuildingPermissionRepository.get_all_by_role_id(
        role_id=must_be_int(role.id), session=session
    )

    assert len(permissions) == 1
    assert permissions[0].role_id == must_be_int(role.id)


def test_permission_repository_update_changes_actions_and_role(
    admin_user: User, role: Role, session: Session
) -> None:
    other_role = Role(name="Other Role", description="", resources=[Resource.BUILDING])
    session.add(other_role)
    session.commit()
    session.refresh(other_role)

    permission = BuildingPermissionRepository.create(
        input=PermissionRegister(
            resource=Resource.BUILDING,
            resource_id=-1,
            actions=[BuildingAction.READ],
            role_id=must_be_int(role.id),
        ),
        user=admin_user,
        session=session,
    )
    session.commit()
    session.refresh(permission)

    updated = BuildingPermissionRepository.update(
        permission=permission,
        input=PermissionUpdate(
            resource=Resource.BUILDING,
            resource_id=-1,
            actions=[BuildingAction.CREATE, BuildingAction.DELETE],
            role_id=must_be_int(other_role.id),
        ),
        user=admin_user,
        session=session,
    )
    session.commit()
    session.refresh(updated)

    assert updated.role_id == must_be_int(other_role.id)
    assert set(updated.actions) == {BuildingAction.CREATE, BuildingAction.DELETE}


def test_permission_repository_delete(admin_user: User, role: Role, session: Session) -> None:
    permission = BuildingPermissionRepository.create(
        input=PermissionRegister(
            resource=Resource.BUILDING,
            resource_id=-1,
            actions=[BuildingAction.READ],
            role_id=must_be_int(role.id),
        ),
        user=admin_user,
        session=session,
    )
    session.commit()
    permission_id = permission.id
    assert permission_id is not None

    BuildingPermissionRepository.delete(id=permission_id, session=session)
    session.commit()

    with pytest.raises(HTTPException):
        BuildingPermissionRepository.get_by_id(id=permission_id, session=session)
