import pytest
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.schedule_db_model import Schedule
from server.models.database.user_db_model import User
from server.services.security.classrooms_permission_checker import (
    ForbiddenClassroomAccess,
)
from server.services.security.role_permission_evaluator import build_permission_index
from server.services.security.schedule_permission_checker import (
    ForbiddenScheduleAccess,
    SchedulePermissionChecker,
)
from server.utils.enums.actions_enums import BuildingAction, ClassroomAction
from server.utils.enums.reservation_type import ReservationType
from server.utils.must_be_int import must_be_int
from tests.factories.model.reservation_model_factory import ReservationModelFactory
from tests.factories.model.schedule_model_factory import ScheduleModelFactory
from tests.factories.model.solicitation_model_factory import SolicitationModelFactory
from tests.utils.permission_test_utils import RolePermissionTestHelper


def test_schedule_checker_admin_bypasses(
    classroom: Classroom, class_: Class, admin_user: User, session: Session
) -> None:
    schedule = ScheduleModelFactory(
        session=session, class_=class_
    ).create_and_refresh(classroom_id=must_be_int(classroom.id), classroom=classroom)
    checker = SchedulePermissionChecker(
        user=admin_user,
        session=session,
        permission_index=build_permission_index(admin_user),
    )
    checker.check_permission(schedule, ClassroomAction.READ)


def test_schedule_checker_with_classroom_denies_without_permission(
    classroom: Classroom, class_: Class, common_user: User, session: Session
) -> None:
    schedule = ScheduleModelFactory(
        session=session, class_=class_
    ).create_and_refresh(classroom_id=must_be_int(classroom.id), classroom=classroom)

    checker = SchedulePermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenClassroomAccess):
        checker.check_permission(schedule, ClassroomAction.READ)


def test_schedule_checker_with_classroom_allows_via_classroom_permission(
    classroom: Classroom,
    class_: Class,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    schedule = ScheduleModelFactory(
        session=session, class_=class_
    ).create_and_refresh(classroom_id=must_be_int(classroom.id), classroom=classroom)

    RolePermissionTestHelper.grant_classroom_permission(
        user=common_user,
        resource_id=must_be_int(classroom.id),
        actions=[ClassroomAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = SchedulePermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(schedule, ClassroomAction.READ)


def test_schedule_checker_class_based_denies_without_building_permission(
    class_: Class, common_user: User, session: Session
) -> None:
    """No classroom allocated yet -> falls back to the class's subject buildings."""
    schedule = ScheduleModelFactory(session=session, class_=class_).create_and_refresh()

    checker = SchedulePermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenScheduleAccess):
        checker.check_permission(schedule, ClassroomAction.READ)


def test_schedule_checker_class_based_allows_via_building_permission(
    building: Building,
    class_: Class,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    schedule = ScheduleModelFactory(session=session, class_=class_).create_and_refresh()

    RolePermissionTestHelper.grant_building_permission(
        user=common_user,
        resource_id=must_be_int(building.id),
        actions=[BuildingAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = SchedulePermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(schedule, ClassroomAction.READ)


def test_schedule_checker_class_based_allows_via_wildcard_building_permission(
    class_: Class, admin_user: User, common_user: User, session: Session
) -> None:
    schedule = ScheduleModelFactory(session=session, class_=class_).create_and_refresh()

    RolePermissionTestHelper.grant_building_permission(
        user=common_user,
        resource_id=-1,
        actions=[BuildingAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = SchedulePermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(schedule, ClassroomAction.READ)


def _create_unallocated_reservation_schedule(
    *, building: Building, creator: User, session: Session
) -> Schedule:
    """A reservation schedule with no classroom, backed by a Solicitation so
    Reservation.get_building() can resolve via the solicitation instead of
    raising - exercising the schedule.reservation branch specifically."""
    reservation = ReservationModelFactory(
        reservation_type=ReservationType.MEETING,
        creator=creator,
        classroom=None,  # type: ignore[arg-type]
        session=session,
    ).create()
    session.commit()
    session.refresh(reservation)
    SolicitationModelFactory(
        building=building, user=creator, reservation=reservation, session=session
    ).create_and_refresh()
    session.refresh(reservation.schedule)
    return reservation.schedule


def test_schedule_checker_reservation_based_denies_without_building_permission(
    building: Building, admin_user: User, common_user: User, session: Session
) -> None:
    schedule = _create_unallocated_reservation_schedule(
        building=building, creator=admin_user, session=session
    )

    checker = SchedulePermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenScheduleAccess):
        checker.check_permission(schedule, ClassroomAction.READ)


def test_schedule_checker_reservation_based_allows_via_building_permission(
    building: Building, admin_user: User, common_user: User, session: Session
) -> None:
    schedule = _create_unallocated_reservation_schedule(
        building=building, creator=admin_user, session=session
    )

    RolePermissionTestHelper.grant_building_permission(
        user=common_user,
        resource_id=must_be_int(building.id),
        actions=[BuildingAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = SchedulePermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(schedule, ClassroomAction.READ)


def test_schedule_checker_id_dispatch_matches_object_dispatch(
    classroom: Classroom, class_: Class, common_user: User, session: Session
) -> None:
    schedule = ScheduleModelFactory(
        session=session, class_=class_
    ).create_and_refresh(classroom_id=must_be_int(classroom.id), classroom=classroom)

    checker = SchedulePermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenClassroomAccess):
        checker.check_permission(must_be_int(schedule.id), ClassroomAction.READ)


def test_schedule_checker_list_denies_when_any_schedule_disallowed(
    classroom: Classroom, class_: Class, admin_user: User, common_user: User, session: Session
) -> None:
    """Grants access to `classroom` only, so schedule_a (allocated to it) is
    individually allowed while schedule_b (unallocated, building ungranted)
    is not - proving the list check evaluates every item rather than
    short-circuiting once it finds one allowed entry."""
    schedule_a = ScheduleModelFactory(
        session=session, class_=class_
    ).create_and_refresh(classroom_id=must_be_int(classroom.id), classroom=classroom)
    schedule_b = ScheduleModelFactory(session=session, class_=class_).create_and_refresh()

    RolePermissionTestHelper.grant_classroom_permission(
        user=common_user,
        resource_id=must_be_int(classroom.id),
        actions=[ClassroomAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = SchedulePermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises((ForbiddenClassroomAccess, ForbiddenScheduleAccess)):
        checker.check_permission([schedule_a, schedule_b], ClassroomAction.READ)
