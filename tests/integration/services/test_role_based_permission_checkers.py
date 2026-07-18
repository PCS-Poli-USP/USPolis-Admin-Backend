import pytest
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.reservation_db_model import Reservation
from server.models.database.role_db_model import Role
from server.models.database.user_db_model import User
from server.models.database.user_role_db_model import UserRole
from server.repositories.building_permission_repository import (
    BuildingPermissionRepository,
)
from server.repositories.classroom_permission_repository import (
    ClassroomPermissionRepository,
)
from server.services.security.buildings_permission_checker import (
    BuildingPermissionChecker,
    ForbiddenBuildingAccess,
)
from server.services.security.class_permission_checker import (
    ClassPermissionChecker,
    ForbiddenClassAccess,
)
from server.services.security.classrooms_permission_checker import (
    ClassroomPermissionChecker,
    ForbiddenClassroomAccess,
)
from server.services.security.reservation_permission_checker import (
    ReservationPermissionChecker,
)
from server.services.security.role_permission_evaluator import build_permission_index
from server.utils.enums.actions_enums import BuildingAction, ClassroomAction
from server.utils.enums.reservation_type import ReservationType
from server.utils.enums.resources_enums import Resource
from server.utils.must_be_int import must_be_int
from tests.factories.model.reservation_model_factory import ReservationModelFactory
from tests.factories.model.role_model_factory import RoleModelFactory
from tests.factories.request.permission_request_factory import (
    PermissionRequestFactory,
)


def _assign_role(*, user: User, role: Role, session: Session) -> None:
    session.add(
        UserRole(
            user_id=must_be_int(user.id),
            role_id=must_be_int(role.id),
            granted_by_id=must_be_int(user.id),
        )
    )
    session.commit()
    session.refresh(user)


def test_building_checker_denies_without_group_or_role(
    building: Building, common_user: User, session: Session
) -> None:
    checker = BuildingPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )

    with pytest.raises(ForbiddenBuildingAccess):
        checker.check_permission(must_be_int(building.id), BuildingAction.READ)


def test_building_checker_allows_via_role_permission(
    building: Building, common_user: User, session: Session
) -> None:
    role = RoleModelFactory(
        session=session, resources=[Resource.BUILDING]
    ).create_and_refresh()
    permission_input = PermissionRequestFactory(
        role=role, resource=Resource.BUILDING
    ).create_input(resource_id=must_be_int(building.id), actions=[BuildingAction.READ])
    BuildingPermissionRepository.create(
        input=permission_input, user=common_user, session=session
    )
    _assign_role(user=common_user, role=role, session=session)

    checker = BuildingPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(must_be_int(building.id), BuildingAction.READ)


def test_building_checker_denies_creation_without_role(
    common_user: User, session: Session
) -> None:
    checker = BuildingPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )

    with pytest.raises(ForbiddenBuildingAccess):
        checker.check_creation_permission(BuildingAction.CREATE)


def test_building_checker_allows_creation_via_wildcard_role_permission(
    common_user: User, session: Session
) -> None:
    role = RoleModelFactory(
        session=session, resources=[Resource.BUILDING]
    ).create_and_refresh()
    permission_input = PermissionRequestFactory(
        role=role, resource=Resource.BUILDING
    ).create_input(resource_id=-1, actions=[BuildingAction.CREATE])
    BuildingPermissionRepository.create(
        input=permission_input, user=common_user, session=session
    )
    _assign_role(user=common_user, role=role, session=session)

    checker = BuildingPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_creation_permission(BuildingAction.CREATE)


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
    classroom: Classroom, common_user: User, session: Session
) -> None:
    role = RoleModelFactory(
        session=session, resources=[Resource.CLASSROOM]
    ).create_and_refresh()
    permission_input = PermissionRequestFactory(
        role=role, resource=Resource.CLASSROOM
    ).create_input(
        resource_id=must_be_int(classroom.id), actions=[ClassroomAction.UPDATE]
    )
    ClassroomPermissionRepository.create(
        input=permission_input, user=common_user, session=session
    )
    _assign_role(user=common_user, role=role, session=session)

    checker = ClassroomPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(must_be_int(classroom.id), ClassroomAction.UPDATE)


def test_classroom_checker_allows_via_building_permission_cascade(
    building: Building, classroom: Classroom, common_user: User, session: Session
) -> None:
    role = RoleModelFactory(
        session=session, resources=[Resource.BUILDING]
    ).create_and_refresh()
    permission_input = PermissionRequestFactory(
        role=role, resource=Resource.BUILDING
    ).create_input(
        resource_id=must_be_int(building.id), actions=[BuildingAction.DELETE]
    )
    BuildingPermissionRepository.create(
        input=permission_input, user=common_user, session=session
    )
    _assign_role(user=common_user, role=role, session=session)

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
    classroom: Classroom, user: User, common_user: User, session: Session
) -> None:
    reservation = _create_reservation_with_classroom(
        classroom=classroom, creator=user, session=session
    )

    checker = ReservationPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenClassroomAccess):
        checker.check_permission(reservation, ClassroomAction.READ)


def test_reservation_checker_allows_via_classroom_permission(
    classroom: Classroom, user: User, common_user: User, session: Session
) -> None:
    reservation = _create_reservation_with_classroom(
        classroom=classroom, creator=user, session=session
    )

    role = RoleModelFactory(
        session=session, resources=[Resource.CLASSROOM]
    ).create_and_refresh()
    permission_input = PermissionRequestFactory(
        role=role, resource=Resource.CLASSROOM
    ).create_input(
        resource_id=must_be_int(classroom.id), actions=[ClassroomAction.READ]
    )
    ClassroomPermissionRepository.create(
        input=permission_input, user=common_user, session=session
    )
    _assign_role(user=common_user, role=role, session=session)

    checker = ReservationPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(reservation, ClassroomAction.READ)


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
    class_: Class, building: Building, common_user: User, session: Session
) -> None:
    role = RoleModelFactory(
        session=session, resources=[Resource.BUILDING]
    ).create_and_refresh()
    permission_input = PermissionRequestFactory(
        role=role, resource=Resource.BUILDING
    ).create_input(resource_id=must_be_int(building.id), actions=[BuildingAction.READ])
    BuildingPermissionRepository.create(
        input=permission_input, user=common_user, session=session
    )
    _assign_role(user=common_user, role=role, session=session)

    checker = ClassPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    # The class's only schedule is unallocated, so once the building-level
    # check passes, the schedule-level check passes too automatically.
    checker.check_permission(class_, ClassroomAction.READ)
