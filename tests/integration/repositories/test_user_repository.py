import pytest
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session

from fastapi import HTTPException

from server.models.database.building_db_model import Building
from server.models.database.role_db_model import Role
from server.models.database.user_db_model import User
from server.models.database.user_role_db_model import UserRole
from server.repositories.user_repository import UserRepository
from server.services.auth.auth_user_info import AuthUserInfo
from server.utils.must_be_int import must_be_int
from tests.factories.model.course_model_factory import CourseModelFactory
from tests.factories.model.curriculum_model_factory import CurriculumModelFactory
from tests.factories.model.group_model_factory import GroupModelFactory
from tests.factories.model.user_model_factory import UserModelFactory
from tests.factories.request.user_request_factory import UserRequestFactory


def test_get_by_id_returns_the_matching_user(
    admin_user: User, session: Session
) -> None:
    found = UserRepository.get_by_id(user_id=must_be_int(admin_user.id), session=session)

    assert found.id == admin_user.id
    assert found.email == admin_user.email


def test_get_by_id_raises_when_user_does_not_exist(session: Session) -> None:
    with pytest.raises(NoResultFound):
        UserRepository.get_by_id(user_id=999999, session=session)


def test_get_by_ids_returns_only_the_matching_users(
    admin_user: User, session: Session
) -> None:
    other = UserModelFactory(session=session).create_and_refresh()

    users = UserRepository.get_by_ids(
        ids=[must_be_int(admin_user.id), must_be_int(other.id)], session=session
    )

    assert {u.id for u in users} == {admin_user.id, other.id}


def test_get_by_email_returns_the_matching_user(
    admin_user: User, session: Session
) -> None:
    found = UserRepository.get_by_email(email=admin_user.email, session=session)

    assert found.id == admin_user.id


def test_get_by_email_raises_when_user_does_not_exist(session: Session) -> None:
    with pytest.raises(NoResultFound):
        UserRepository.get_by_email(email="does-not-exist@usp.br", session=session)


def test_get_all_returns_every_user(admin_user: User, session: Session) -> None:
    other = UserModelFactory(session=session).create_and_refresh()

    users = UserRepository.get_all(session=session)

    ids = {u.id for u in users}
    assert admin_user.id in ids
    assert other.id in ids


def test_get_all_on_building_returns_only_users_linked_to_it(
    admin_user: User, building: Building, session: Session
) -> None:
    linked = UserModelFactory(session=session).create_and_refresh(buildings=[building])
    unlinked = UserModelFactory(session=session).create_and_refresh()

    users = UserRepository.get_all_on_building(
        building_id=must_be_int(building.id), session=session
    )

    ids = {u.id for u in users}
    assert linked.id in ids
    assert unlinked.id not in ids


def test_get_admin_users_returns_only_admin_users(
    admin_user: User, common_user: User, session: Session
) -> None:
    admins = UserRepository.get_admin_users(session=session)

    ids = {u.id for u in admins}
    assert admin_user.id in ids
    assert common_user.id not in ids


def _grant_role(*, user: User, role: Role, granted_by: User, session: Session) -> None:
    session.add(
        UserRole(
            user_id=must_be_int(user.id),
            role_id=must_be_int(role.id),
            granted_by_id=must_be_int(granted_by.id),
        )
    )
    session.commit()


def test_get_all_with_permissions_includes_role_permissions(
    admin_user: User, role: Role, session: Session
) -> None:
    _grant_role(user=admin_user, role=role, granted_by=admin_user, session=session)

    users = UserRepository.get_all_with_permissions(session=session)

    found = next(u for u in users if u.id == admin_user.id)
    assert [r.id for r in found.roles] == [role.id]


def test_get_with_permissions_includes_role_permissions(
    admin_user: User, role: Role, session: Session
) -> None:
    _grant_role(user=admin_user, role=role, granted_by=admin_user, session=session)

    found = UserRepository.get_with_permissions(
        user_id=must_be_int(admin_user.id), session=session
    )

    assert [r.id for r in found.roles] == [role.id]


def test_create_without_groups_has_no_buildings(session: Session) -> None:
    input = UserRequestFactory().create_input()

    user = UserRepository.create(creator=None, input=input, session=session)
    session.commit()
    session.refresh(user)

    assert user.name == input.name
    assert user.email == input.email
    assert user.buildings == []
    assert user.groups == []


def test_create_with_groups_derives_buildings_from_them(
    admin_user: User, building: Building, session: Session
) -> None:
    group = GroupModelFactory(building=building, session=session).create_and_refresh()
    input = UserRequestFactory().create_input(group_ids=[must_be_int(group.id)])

    user = UserRepository.create(creator=admin_user, input=input, session=session)
    session.commit()
    session.refresh(user)

    assert [g.id for g in user.groups] == [group.id]
    assert [b.id for b in user.buildings or []] == [building.id]
    assert user.created_by_id == admin_user.id


def test_get_from_auth_returns_the_existing_user_for_a_known_email(
    admin_user: User, session: Session
) -> None:
    auth_info = AuthUserInfo(
        email=admin_user.email,
        email_verified=True,
        domain=admin_user.email.split("@")[1],
        name=admin_user.name,
        picture="https://example.com/pic.png",
        given_name=admin_user.name,
        family_name="",
    )

    user = UserRepository.get_from_auth(user_info=auth_info, session=session)

    assert user.id == admin_user.id


def test_get_from_auth_creates_a_new_user_for_an_unknown_email(
    session: Session,
) -> None:
    auth_info = AuthUserInfo(
        email="new-user@usp.br",
        email_verified=True,
        domain="usp.br",
        name="Novo Usuário",
        picture="https://example.com/pic.png",
        given_name="Novo",
        family_name="Usuário",
    )

    user = UserRepository.get_from_auth(user_info=auth_info, session=session)

    assert user.email == "new-user@usp.br"
    assert user.is_admin is False
    assert UserRepository.get_by_email(email="new-user@usp.br", session=session).id == (
        user.id
    )


def test_update_changes_admin_status_and_groups(
    admin_user: User, building: Building, session: Session
) -> None:
    target = UserModelFactory(session=session).create_and_refresh(is_admin=False)
    group = GroupModelFactory(building=building, session=session).create_and_refresh()
    input = UserRequestFactory().update_input(
        is_admin=True, group_ids=[must_be_int(group.id)]
    )

    updated = UserRepository.update(
        requester=admin_user, id=must_be_int(target.id), input=input, session=session
    )
    session.commit()
    session.refresh(updated)

    assert updated.is_admin is True
    assert [g.id for g in updated.groups] == [group.id]


def test_update_forbids_changing_own_admin_status(
    admin_user: User, session: Session
) -> None:
    input = UserRequestFactory().update_input(is_admin=not admin_user.is_admin)

    with pytest.raises(HTTPException):
        UserRepository.update(
            requester=admin_user,
            id=must_be_int(admin_user.id),
            input=input,
            session=session,
        )


def test_update_allows_keeping_own_admin_status_unchanged(
    admin_user: User, session: Session
) -> None:
    input = UserRequestFactory().update_input(is_admin=admin_user.is_admin)

    updated = UserRepository.update(
        requester=admin_user,
        id=must_be_int(admin_user.id),
        input=input,
        session=session,
    )

    assert updated.id == admin_user.id


def test_update_email_notifications(session: Session) -> None:
    user = UserModelFactory(session=session).create_and_refresh(receive_emails=True)

    updated = UserRepository.update_email_notifications(
        user=user, receive_emails=False, session=session
    )
    session.commit()
    session.refresh(updated)

    assert updated.receive_emails is False


def test_visit_user_updates_last_visited(session: Session) -> None:
    user = UserModelFactory(session=session).create_and_refresh()
    original_last_visited = user.last_visited

    updated = UserRepository.visit_user(user=user, session=session)
    session.commit()
    session.refresh(updated)

    assert updated.last_visited >= original_last_visited


def test_update_curriculum_sets_the_users_curriculum(
    admin_user: User, session: Session
) -> None:
    user = UserModelFactory(session=session).create_and_refresh()
    course = CourseModelFactory(
        creator=admin_user, session=session
    ).create_and_refresh()
    curriculum = CurriculumModelFactory(
        course=course, creator=admin_user, session=session
    ).create_and_refresh()

    updated = UserRepository.update_curriculum(
        user=user, curriculum_id=must_be_int(curriculum.id), session=session
    )
    session.commit()
    session.refresh(updated)

    assert updated.curriculum_id == curriculum.id


def test_update_curriculum_raises_for_an_unknown_curriculum(session: Session) -> None:
    user = UserModelFactory(session=session).create_and_refresh()

    with pytest.raises(HTTPException):
        UserRepository.update_curriculum(
            user=user, curriculum_id=999999, session=session
        )
