import pytest
from sqlmodel import Session, select

from server.models.database.classroom_permission_db_model import ClassroomPermission
from server.models.database.role_db_model import Role
from server.models.database.user_db_model import User
from server.models.database.user_role_db_model import UserRole
from server.repositories.classroom_permission_repository import (
    ClassroomPermissionRepository,
)
from server.repositories.role_repository import RoleNotFound, RoleRepository
from server.utils.enums.resources_enums import Resource
from server.utils.must_be_int import must_be_int
from tests.factories.request.permission_request_factory import (
    PermissionRequestFactory,
)
from tests.factories.request.role_request_factory import RoleRequestFactory


def test_create_role_without_permissions(admin_user: User, session: Session) -> None:
    input = RoleRequestFactory(resources=[]).create_input()

    role = RoleRepository.create(input=input, user=admin_user, session=session)
    session.commit()
    session.refresh(role)

    assert role.name == input.name
    assert role.resources == []
    assert role.get_permissions() == []


def test_create_role_with_permissions(admin_user: User, session: Session) -> None:
    factory = RoleRequestFactory(resources=[Resource.CLASSROOM, Resource.COURSE])
    input = factory.create_input(
        permissions=[
            factory.build_permission(Resource.CLASSROOM),
            factory.build_permission(Resource.COURSE),
        ]
    )

    role = RoleRepository.create(input=input, user=admin_user, session=session)
    session.commit()
    session.refresh(role)

    assert len(role.classroom_permissions) == 1
    assert len(role.course_permissions) == 1
    assert role.classroom_permissions[0].role_id == role.id
    assert role.course_permissions[0].role_id == role.id


def test_create_role_deduplicates_repeated_permissions(
    admin_user: User, session: Session
) -> None:
    factory = RoleRequestFactory(resources=[Resource.CLASSROOM])
    permission = factory.build_permission(Resource.CLASSROOM)
    input = factory.create_input(permissions=[permission, permission])

    role = RoleRepository.create(input=input, user=admin_user, session=session)
    session.commit()
    session.refresh(role)

    assert len(role.classroom_permissions) == 1


def test_update_role_adds_new_permission(
    admin_user: User, role: Role, session: Session
) -> None:
    factory = RoleRequestFactory(resources=role.resources)
    input = factory.update_input(
        name=role.name,
        description=role.description,
        resources=role.resources,
        permissions=[factory.build_permission(Resource.CLASSROOM)],
    )

    updated = RoleRepository.update(
        id=must_be_int(role.id), input=input, user=admin_user, session=session
    )
    session.commit()
    session.refresh(updated)

    assert len(updated.classroom_permissions) == 1


def test_update_role_removes_missing_permission(
    admin_user: User, role: Role, session: Session
) -> None:
    factory = RoleRequestFactory(resources=role.resources)
    create_input = factory.update_input(
        name=role.name,
        description=role.description,
        resources=role.resources,
        permissions=[factory.build_permission(Resource.CLASSROOM)],
    )
    role = RoleRepository.update(
        id=must_be_int(role.id), input=create_input, user=admin_user, session=session
    )
    session.commit()
    session.refresh(role)
    assert len(role.classroom_permissions) == 1

    empty_input = factory.update_input(
        name=role.name,
        description=role.description,
        resources=role.resources,
        permissions=[],
    )
    updated = RoleRepository.update(
        id=must_be_int(role.id), input=empty_input, user=admin_user, session=session
    )
    session.commit()
    session.refresh(updated)

    assert updated.classroom_permissions == []


def test_update_role_keeps_unchanged_permission(
    admin_user: User, role: Role, session: Session
) -> None:
    factory = RoleRequestFactory(resources=role.resources)
    permission = factory.build_permission(Resource.CLASSROOM)
    input = factory.update_input(
        name=role.name,
        description=role.description,
        resources=role.resources,
        permissions=[permission],
    )

    role = RoleRepository.update(
        id=must_be_int(role.id), input=input, user=admin_user, session=session
    )
    session.commit()
    session.refresh(role)
    first_permission_id = role.classroom_permissions[0].id

    updated = RoleRepository.update(
        id=must_be_int(role.id), input=input, user=admin_user, session=session
    )
    session.commit()
    session.refresh(updated)

    assert len(updated.classroom_permissions) == 1
    assert updated.classroom_permissions[0].id == first_permission_id


def test_delete_role_deletes_permissions_and_user_links(
    admin_user: User, role: Role, session: Session
) -> None:
    permission_input = PermissionRequestFactory(
        role=role, resource=Resource.CLASSROOM
    ).create_input()
    permission = ClassroomPermissionRepository.create(
        input=permission_input, user=admin_user, session=session
    )
    session.commit()
    permission_id = must_be_int(permission.id)

    session.add(
        UserRole(
            user_id=must_be_int(admin_user.id),
            role_id=must_be_int(role.id),
            granted_by_id=must_be_int(admin_user.id),
        )
    )
    session.commit()

    RoleRepository.delete(id=must_be_int(role.id), session=session)
    session.commit()

    with pytest.raises(RoleNotFound):
        RoleRepository.get_by_id(id=must_be_int(role.id), session=session)

    remaining_permission = session.exec(
        select(ClassroomPermission).where(ClassroomPermission.id == permission_id)
    ).first()
    assert remaining_permission is None

    remaining_links = session.exec(
        select(UserRole).where(UserRole.role_id == role.id)
    ).all()
    assert list(remaining_links) == []


def test_get_all_filters_by_resource(admin_user: User, session: Session) -> None:
    classroom_only = RoleRequestFactory(resources=[Resource.CLASSROOM]).create_input()
    course_only = RoleRequestFactory(resources=[Resource.COURSE]).create_input()

    RoleRepository.create(input=classroom_only, user=admin_user, session=session)
    RoleRepository.create(input=course_only, user=admin_user, session=session)
    session.commit()

    roles = RoleRepository.get_all(session=session, resources=[Resource.CLASSROOM])

    assert len(roles) == 1
    assert roles[0].name == classroom_only.name


def test_get_all_without_a_filter_returns_every_role(
    admin_user: User, session: Session
) -> None:
    classroom_only = RoleRequestFactory(resources=[Resource.CLASSROOM]).create_input()
    course_only = RoleRequestFactory(resources=[Resource.COURSE]).create_input()

    RoleRepository.create(input=classroom_only, user=admin_user, session=session)
    RoleRepository.create(input=course_only, user=admin_user, session=session)
    session.commit()

    roles = RoleRepository.get_all(session=session)

    names = {role.name for role in roles}
    assert {classroom_only.name, course_only.name} <= names


def test_get_by_id_returns_the_matching_role(role: Role, session: Session) -> None:
    found = RoleRepository.get_by_id(id=must_be_int(role.id), session=session)

    assert found.id == role.id
    assert found.name == role.name


def test_get_by_id_raises_when_role_does_not_exist(session: Session) -> None:
    with pytest.raises(RoleNotFound):
        RoleRepository.get_by_id(id=999999, session=session)
