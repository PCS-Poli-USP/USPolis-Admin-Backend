import pytest
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.group_db_model import Group
from server.models.database.user_db_model import User
from server.services.security.group_permission_checker import (
    ForbiddenGroupAccess,
    GroupPermissionChecker,
)
from server.utils.must_be_int import must_be_int
from tests.factories.model.group_model_factory import GroupModelFactory


def test_group_checker_admin_bypasses(
    group: Group, admin_user: User, session: Session
) -> None:
    checker = GroupPermissionChecker(user=admin_user, session=session)
    checker.check_permission(must_be_int(group.id))


def test_group_checker_denies_id_when_not_a_member(
    group: Group, common_user: User, session: Session
) -> None:
    checker = GroupPermissionChecker(user=common_user, session=session)
    with pytest.raises(ForbiddenGroupAccess):
        checker.check_permission(must_be_int(group.id))


def test_group_checker_allows_id_when_a_member(
    building: Building, common_user: User, session: Session
) -> None:
    group = GroupModelFactory(building=building, session=session).create_and_refresh(
        users=[common_user]
    )
    session.refresh(common_user)

    checker = GroupPermissionChecker(user=common_user, session=session)
    checker.check_permission(must_be_int(group.id))


def test_group_checker_denies_obj_when_not_a_member(
    group: Group, common_user: User, session: Session
) -> None:
    checker = GroupPermissionChecker(user=common_user, session=session)
    with pytest.raises(ForbiddenGroupAccess):
        checker.check_permission(group)


def test_group_checker_allows_obj_when_a_member(
    building: Building, common_user: User, session: Session
) -> None:
    group = GroupModelFactory(building=building, session=session).create_and_refresh(
        users=[common_user]
    )
    session.refresh(common_user)

    checker = GroupPermissionChecker(user=common_user, session=session)
    checker.check_permission(group)


def test_group_checker_denies_list_when_missing_one_group(
    building: Building, common_user: User, session: Session
) -> None:
    member_group = GroupModelFactory(
        building=building, session=session
    ).create_and_refresh(users=[common_user])
    other_group = GroupModelFactory(building=building, session=session).create_and_refresh()
    session.refresh(common_user)

    checker = GroupPermissionChecker(user=common_user, session=session)
    with pytest.raises(ForbiddenGroupAccess):
        checker.check_permission([member_group, other_group])


def test_group_checker_allows_list_when_member_of_all(
    building: Building, common_user: User, session: Session
) -> None:
    group_a = GroupModelFactory(building=building, session=session).create_and_refresh(
        users=[common_user]
    )
    group_b = GroupModelFactory(building=building, session=session).create_and_refresh(
        users=[common_user]
    )
    session.refresh(common_user)

    checker = GroupPermissionChecker(user=common_user, session=session)
    checker.check_permission([group_a, group_b])
