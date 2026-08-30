import pytest
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.services.security.role_permission_evaluator import build_permission_index
from server.services.security.subjects_permission_checker import (
    ForbiddenSubjectAccess,
    SubjectPermissionChecker,
)
from server.utils.enums.actions_enums import BuildingAction
from server.utils.must_be_int import must_be_int
from tests.factories.model.building_model_factory import BuildingModelFactory
from tests.factories.model.subject_model_factory import SubjectModelFactory
from tests.utils.permission_test_utils import RolePermissionTestHelper


def test_subject_checker_admin_bypasses(
    subject: Subject, admin_user: User, session: Session
) -> None:
    checker = SubjectPermissionChecker(
        user=admin_user,
        session=session,
        permission_index=build_permission_index(admin_user),
    )
    checker.check_permission(subject, BuildingAction.READ)


def test_subject_checker_denies_without_group_or_role(
    subject: Subject, common_user: User, session: Session
) -> None:
    checker = SubjectPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenSubjectAccess):
        checker.check_permission(subject, BuildingAction.READ)


def test_subject_checker_allows_via_building_permission(
    subject: Subject,
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

    checker = SubjectPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(subject, BuildingAction.READ)


def test_subject_checker_allows_via_wildcard_building_permission(
    subject: Subject,
    building: Building,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    RolePermissionTestHelper.grant_building_permission(
        user=common_user,
        resource_id=-1,
        actions=[BuildingAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = SubjectPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(subject, BuildingAction.READ)


def test_subject_checker_id_dispatch_matches_object_dispatch(
    subject: Subject, common_user: User, session: Session
) -> None:
    checker = SubjectPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenSubjectAccess):
        checker.check_permission(must_be_int(subject.id), BuildingAction.READ)


def test_subject_checker_list_denies_when_any_subject_disallowed(
    subject: Subject,
    building: Building,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    """Grants access to `subject`'s own building only, so `subject` is
    individually allowed while `other_subject` (a different, ungranted
    building) is not - proving the list check evaluates every item rather
    than short-circuiting once it finds one allowed entry."""
    other_building = BuildingModelFactory(
        creator=admin_user, session=session
    ).create_and_refresh()
    other_subject = SubjectModelFactory(
        building=other_building, session=session
    ).create_and_refresh()
    RolePermissionTestHelper.grant_building_permission(
        user=common_user,
        resource_id=must_be_int(building.id),
        actions=[BuildingAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = SubjectPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenSubjectAccess):
        checker.check_permission([subject, other_subject], BuildingAction.READ)


def test_subject_checker_list_allows_when_all_subjects_allowed(
    subject: Subject,
    building: Building,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    other_subject = SubjectModelFactory(
        building=building, session=session
    ).create_and_refresh()
    RolePermissionTestHelper.grant_building_permission(
        user=common_user,
        resource_id=must_be_int(building.id),
        actions=[BuildingAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = SubjectPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission([subject, other_subject], BuildingAction.READ)
