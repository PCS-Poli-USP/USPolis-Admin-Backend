import pytest
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.group_db_model import Group
from server.models.database.reservation_db_model import Reservation
from server.models.database.user_db_model import User
from server.services.security.buildings_permission_checker import (
    ForbiddenBuildingAccess,
)
from server.services.security.classrooms_permission_checker import (
    ForbiddenClassroomAccess,
)
from server.services.security.reservation_permission_checker import (
    ReservationPermissionChecker,
)
from server.services.security.role_permission_evaluator import build_permission_index
from server.utils.enums.actions_enums import BuildingAction, ClassroomAction
from server.utils.enums.reservation_type import ReservationType
from server.utils.must_be_int import must_be_int
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.model.reservation_model_factory import ReservationModelFactory
from tests.factories.model.solicitation_model_factory import SolicitationModelFactory
from tests.utils.permission_test_utils import RolePermissionTestHelper


def _create_reservation_with_classroom(
    *, classroom: Classroom, creator: User, session: Session
) -> Reservation:
    reservation = ReservationModelFactory(
        reservation_type=ReservationType.MEETING,
        creator=creator,
        classroom=classroom,
        session=session,
    ).create_and_refresh()
    # ReservationModelFactory auto-creates an unallocated schedule by default;
    # link it to the given classroom so get_classroom()/get_building() resolve.
    reservation.schedule.classroom_id = must_be_int(classroom.id)
    session.add(reservation.schedule)
    session.commit()
    session.refresh(reservation)
    return reservation


def test_reservation_checker_denies_without_group_or_role(
    classroom: Classroom, admin_user: User, common_user: User, session: Session
) -> None:
    reservation = _create_reservation_with_classroom(
        classroom=classroom, creator=admin_user, session=session
    )

    checker = ReservationPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenClassroomAccess):
        checker.check_permission(reservation, ClassroomAction.READ)


def test_reservation_checker_allows_via_classroom_permission(
    classroom: Classroom, admin_user: User, common_user: User, session: Session
) -> None:
    reservation = _create_reservation_with_classroom(
        classroom=classroom, creator=admin_user, session=session
    )

    RolePermissionTestHelper.grant_classroom_permission(
        user=common_user,
        resource_id=must_be_int(classroom.id),
        actions=[ClassroomAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = ReservationPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(reservation, ClassroomAction.READ)


def test_reservation_checker_allows_via_wildcard_classroom_permission(
    classroom: Classroom, admin_user: User, common_user: User, session: Session
) -> None:
    reservation = _create_reservation_with_classroom(
        classroom=classroom, creator=admin_user, session=session
    )

    RolePermissionTestHelper.grant_classroom_permission(
        user=common_user,
        resource_id=-1,
        actions=[ClassroomAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = ReservationPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(reservation, ClassroomAction.READ)


def test_reservation_checker_admin_bypasses(
    classroom: Classroom, admin_user: User, session: Session
) -> None:
    reservation = _create_reservation_with_classroom(
        classroom=classroom, creator=admin_user, session=session
    )
    checker = ReservationPermissionChecker(
        user=admin_user,
        session=session,
        permission_index=build_permission_index(admin_user),
    )
    checker.check_permission(reservation, ClassroomAction.READ)


def test_reservation_checker_id_dispatch_matches_object_dispatch(
    classroom: Classroom, admin_user: User, common_user: User, session: Session
) -> None:
    reservation = _create_reservation_with_classroom(
        classroom=classroom, creator=admin_user, session=session
    )
    checker = ReservationPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenClassroomAccess):
        checker.check_permission(must_be_int(reservation.id), ClassroomAction.READ)


def test_reservation_checker_list_denies_when_any_reservation_disallowed(
    building: Building,
    classroom: Classroom,
    group: Group,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    """Grants access to `classroom` only, so reservation_a (booked in it) is
    individually allowed while reservation_b (a different, ungranted
    classroom) is not - proving the list check evaluates every item rather
    than short-circuiting once it finds one allowed entry."""
    other_classroom = ClassroomModelFactory(
        creator=admin_user, building=building, group=group, session=session
    ).create_and_refresh()
    reservation_a = _create_reservation_with_classroom(
        classroom=classroom, creator=admin_user, session=session
    )
    reservation_b = _create_reservation_with_classroom(
        classroom=other_classroom, creator=admin_user, session=session
    )
    RolePermissionTestHelper.grant_classroom_permission(
        user=common_user,
        resource_id=must_be_int(classroom.id),
        actions=[ClassroomAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = ReservationPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenClassroomAccess):
        checker.check_permission(
            [reservation_a, reservation_b], ClassroomAction.READ
        )


def _create_reservation_without_classroom(
    *, building: Building, creator: User, session: Session
) -> Reservation:
    """A reservation with no classroom, backed by a Solicitation so
    Reservation.get_building() can resolve via the solicitation instead of
    raising - exercising the checker's building-fallback branch."""
    reservation = ReservationModelFactory(
        reservation_type=ReservationType.MEETING,
        creator=creator,
        classroom=None,  # type: ignore[arg-type]
        session=session,
    ).create_and_refresh()
    SolicitationModelFactory(
        building=building, user=creator, reservation=reservation, session=session
    ).create_and_refresh()
    session.refresh(reservation)
    return reservation


def test_reservation_checker_without_classroom_denies_without_building_permission(
    building: Building, admin_user: User, common_user: User, session: Session
) -> None:
    reservation = _create_reservation_without_classroom(
        building=building, creator=admin_user, session=session
    )
    checker = ReservationPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenBuildingAccess):
        checker.check_permission(reservation, ClassroomAction.READ)


def test_reservation_checker_without_classroom_allows_via_building_permission(
    building: Building, admin_user: User, common_user: User, session: Session
) -> None:
    reservation = _create_reservation_without_classroom(
        building=building, creator=admin_user, session=session
    )
    RolePermissionTestHelper.grant_building_permission(
        user=common_user,
        resource_id=must_be_int(building.id),
        actions=[BuildingAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = ReservationPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(reservation, ClassroomAction.READ)
