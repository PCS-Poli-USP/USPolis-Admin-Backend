import pytest
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.solicitation_db_model import Solicitation
from server.models.database.user_db_model import User
from server.services.security.buildings_permission_checker import (
    ForbiddenBuildingAccess,
)
from server.services.security.classrooms_permission_checker import (
    ForbiddenClassroomAccess,
)
from server.services.security.role_permission_evaluator import build_permission_index
from server.services.security.solicitation_permission_checker import (
    SolicitationPermissionChecker,
)
from server.utils.enums.actions_enums import BuildingAction, ClassroomAction
from server.utils.enums.reservation_type import ReservationType
from server.utils.must_be_int import must_be_int
from tests.factories.model.reservation_model_factory import ReservationModelFactory
from tests.factories.model.solicitation_model_factory import SolicitationModelFactory
from tests.utils.permission_test_utils import RolePermissionTestHelper


def _create_solicitation_with_classroom(
    *, building: Building, classroom: Classroom, creator: User, session: Session
) -> Solicitation:
    reservation = ReservationModelFactory(
        reservation_type=ReservationType.MEETING,
        creator=creator,
        classroom=classroom,
        session=session,
    ).create_and_refresh()
    reservation.schedule.classroom_id = must_be_int(classroom.id)
    session.add(reservation.schedule)
    session.commit()
    session.refresh(reservation)
    return SolicitationModelFactory(
        building=building,
        user=creator,
        reservation=reservation,
        solicited_classroom=classroom,
        session=session,
    ).create_and_refresh(required_classroom=True)


def _create_solicitation_without_classroom(
    *, building: Building, creator: User, session: Session
) -> Solicitation:
    reservation = ReservationModelFactory(
        reservation_type=ReservationType.MEETING,
        creator=creator,
        classroom=None,  # type: ignore[arg-type]
        session=session,
    ).create_and_refresh()
    return SolicitationModelFactory(
        building=building, user=creator, reservation=reservation, session=session
    ).create_and_refresh(required_classroom=False)


def test_solicitation_checker_admin_bypasses(
    building: Building, classroom: Classroom, admin_user: User, session: Session
) -> None:
    solicitation = _create_solicitation_with_classroom(
        building=building, classroom=classroom, creator=admin_user, session=session
    )
    checker = SolicitationPermissionChecker(
        user=admin_user,
        session=session,
        permission_index=build_permission_index(admin_user),
    )
    checker.check_permission(solicitation, ClassroomAction.READ)


def test_solicitation_checker_with_classroom_denies_without_permission(
    building: Building,
    classroom: Classroom,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    solicitation = _create_solicitation_with_classroom(
        building=building, classroom=classroom, creator=admin_user, session=session
    )
    checker = SolicitationPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenClassroomAccess):
        checker.check_permission(solicitation, ClassroomAction.READ)


def test_solicitation_checker_with_classroom_allows_via_classroom_permission(
    building: Building,
    classroom: Classroom,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    solicitation = _create_solicitation_with_classroom(
        building=building, classroom=classroom, creator=admin_user, session=session
    )
    RolePermissionTestHelper.grant_classroom_permission(
        user=common_user,
        resource_id=must_be_int(classroom.id),
        actions=[ClassroomAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = SolicitationPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(solicitation, ClassroomAction.READ)


def test_solicitation_checker_with_classroom_allows_via_wildcard_permission(
    building: Building,
    classroom: Classroom,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    solicitation = _create_solicitation_with_classroom(
        building=building, classroom=classroom, creator=admin_user, session=session
    )
    RolePermissionTestHelper.grant_classroom_permission(
        user=common_user,
        resource_id=-1,
        actions=[ClassroomAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = SolicitationPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(solicitation, ClassroomAction.READ)


def test_solicitation_checker_without_classroom_denies_without_building_permission(
    building: Building, admin_user: User, common_user: User, session: Session
) -> None:
    solicitation = _create_solicitation_without_classroom(
        building=building, creator=admin_user, session=session
    )
    checker = SolicitationPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenBuildingAccess):
        checker.check_permission(solicitation, ClassroomAction.READ)


def test_solicitation_checker_without_classroom_allows_via_building_permission(
    building: Building, admin_user: User, common_user: User, session: Session
) -> None:
    solicitation = _create_solicitation_without_classroom(
        building=building, creator=admin_user, session=session
    )
    RolePermissionTestHelper.grant_building_permission(
        user=common_user,
        resource_id=must_be_int(building.id),
        actions=[BuildingAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = SolicitationPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(solicitation, ClassroomAction.READ)


def test_solicitation_checker_id_dispatch_matches_object_dispatch(
    building: Building,
    classroom: Classroom,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    solicitation = _create_solicitation_with_classroom(
        building=building, classroom=classroom, creator=admin_user, session=session
    )
    checker = SolicitationPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenClassroomAccess):
        checker.check_permission(must_be_int(solicitation.id), ClassroomAction.READ)


def test_solicitation_checker_list_denies_when_any_solicitation_disallowed(
    building: Building,
    classroom: Classroom,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    solicitation_a = _create_solicitation_with_classroom(
        building=building, classroom=classroom, creator=admin_user, session=session
    )
    solicitation_b = _create_solicitation_without_classroom(
        building=building, creator=admin_user, session=session
    )
    RolePermissionTestHelper.grant_classroom_permission(
        user=common_user,
        resource_id=must_be_int(classroom.id),
        actions=[ClassroomAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = SolicitationPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises((ForbiddenClassroomAccess, ForbiddenBuildingAccess)):
        checker.check_permission(
            [solicitation_a, solicitation_b], ClassroomAction.READ
        )
