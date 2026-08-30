import pytest
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.group_db_model import Group
from server.models.database.user_db_model import User
from server.services.security.classrooms_permission_checker import (
    ClassroomPermissionChecker,
    ForbiddenClassroomAccess,
)
from server.services.security.role_permission_evaluator import build_permission_index
from server.utils.enums.actions_enums import BuildingAction, ClassroomAction
from server.utils.must_be_int import must_be_int
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.utils.permission_test_utils import RolePermissionTestHelper


def test_classroom_checker_denies_without_group_or_role(
    classroom: Classroom, common_user: User, session: Session
) -> None:
    checker = ClassroomPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )

    with pytest.raises(ForbiddenClassroomAccess):
        checker.check_permission(must_be_int(classroom.id), ClassroomAction.UPDATE)


def test_classroom_checker_allows_via_direct_classroom_permission(
    classroom: Classroom, admin_user: User, common_user: User, session: Session
) -> None:
    RolePermissionTestHelper.grant_classroom_permission(
        user=common_user,
        resource_id=must_be_int(classroom.id),
        actions=[ClassroomAction.UPDATE],
        granted_by=admin_user,
        session=session,
    )

    checker = ClassroomPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(must_be_int(classroom.id), ClassroomAction.UPDATE)


def test_classroom_checker_allows_via_building_permission_cascade(
    building: Building,
    classroom: Classroom,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    RolePermissionTestHelper.grant_building_permission(
        user=common_user,
        resource_id=must_be_int(building.id),
        actions=[BuildingAction.DELETE],
        granted_by=admin_user,
        session=session,
    )

    checker = ClassroomPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    # Granted action (DELETE) cascades from the building permission.
    checker.check_permission(must_be_int(classroom.id), ClassroomAction.DELETE)

    # A different, non-granted action does not.
    with pytest.raises(ForbiddenClassroomAccess):
        checker.check_permission(must_be_int(classroom.id), ClassroomAction.RESERVE)


def test_classroom_checker_list_denies_when_any_classroom_disallowed(
    building: Building,
    classroom: Classroom,
    group: Group,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    other_classroom = ClassroomModelFactory(
        creator=admin_user, building=building, group=group, session=session
    ).create_and_refresh()
    RolePermissionTestHelper.grant_classroom_permission(
        user=common_user,
        resource_id=must_be_int(classroom.id),
        actions=[ClassroomAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = ClassroomPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    # Granted for `classroom` only - `other_classroom` is not, so the list
    # check should still raise, exercising the list-dispatch branch.
    with pytest.raises(ForbiddenClassroomAccess):
        checker.check_permission([classroom, other_classroom], ClassroomAction.READ)


def test_classroom_checker_allows_via_wildcard_role_permission(
    building: Building,
    classroom: Classroom,
    group: Group,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    other_classroom = ClassroomModelFactory(
        creator=admin_user, building=building, group=group, session=session
    ).create_and_refresh()
    RolePermissionTestHelper.grant_classroom_permission(
        user=common_user,
        resource_id=-1,
        actions=[ClassroomAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = ClassroomPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(must_be_int(classroom.id), ClassroomAction.READ)
    checker.check_permission(must_be_int(other_classroom.id), ClassroomAction.READ)
