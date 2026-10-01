import pytest
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.user_db_model import User
from server.services.security.class_permission_checker import (
    ClassPermissionChecker,
    ForbiddenClassAccess,
)
from server.services.security.role_permission_evaluator import build_permission_index
from server.utils.enums.actions_enums import BuildingAction, ClassroomAction
from server.utils.must_be_int import must_be_int
from tests.factories.model.building_model_factory import BuildingModelFactory
from tests.factories.model.class_model_factory import ClassModelFactory
from tests.factories.model.subject_model_factory import SubjectModelFactory
from tests.utils.permission_test_utils import RolePermissionTestHelper


def test_class_checker_denies_without_group_or_role(
    class_: Class, common_user: User, session: Session
) -> None:
    checker = ClassPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenClassAccess):
        checker.check_permission(class_, ClassroomAction.READ)


def test_class_checker_allows_via_building_permission(
    class_: Class,
    building: Building,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    RolePermissionTestHelper.grant_building_permission(
        user=common_user,
        resource_id=must_be_int(building.id),
        actions=[BuildingAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = ClassPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    # The class's only schedule is unallocated, so once the building-level
    # check passes, the schedule-level check passes too automatically.
    checker.check_permission(class_, ClassroomAction.READ)


def test_class_checker_id_dispatch_matches_object_dispatch(
    class_: Class, common_user: User, session: Session
) -> None:
    checker = ClassPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenClassAccess):
        checker.check_permission(must_be_int(class_.id), ClassroomAction.READ)


def test_class_checker_list_denies_when_any_class_disallowed(
    class_: Class,
    building: Building,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    """Grants access to `class_`'s own building only, so `class_` is
    individually allowed while `other_class` (a different, ungranted
    building) is not - proving the list check evaluates every item rather
    than short-circuiting once it finds one allowed entry."""
    other_building = BuildingModelFactory(
        creator=admin_user, session=session
    ).create_and_refresh()
    other_subject = SubjectModelFactory(
        building=other_building, session=session
    ).create_and_refresh()
    other_class = ClassModelFactory(
        subject=other_subject, session=session
    ).create_and_refresh()

    RolePermissionTestHelper.grant_building_permission(
        user=common_user,
        resource_id=must_be_int(building.id),
        actions=[BuildingAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = ClassPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenClassAccess):
        checker.check_permission([class_, other_class], ClassroomAction.READ)


def test_class_checker_allows_via_wildcard_building_permission(
    class_: Class, admin_user: User, common_user: User, session: Session
) -> None:
    """Wildcard grant on BUILDING covers a class in a building that was
    never specifically granted, proving it is a true wildcard and not
    accidentally scoped to the fixture's own building."""
    other_building = BuildingModelFactory(
        creator=admin_user, session=session
    ).create_and_refresh()
    other_subject = SubjectModelFactory(
        building=other_building, session=session
    ).create_and_refresh()
    other_class = ClassModelFactory(
        subject=other_subject, session=session
    ).create_and_refresh()

    RolePermissionTestHelper.grant_building_permission(
        user=common_user,
        resource_id=-1,
        actions=[BuildingAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = ClassPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(class_, ClassroomAction.READ)
    checker.check_permission(other_class, ClassroomAction.READ)
