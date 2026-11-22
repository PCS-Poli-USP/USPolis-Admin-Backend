from typing import Annotated

from fastapi import Depends

from server.deps.access_scope_dep import AccessScopeDep
from server.deps.authenticate import UserDep
from server.deps.interval_dep import QueryIntervalDep
from server.deps.permission_index_dep import PermissionIndexDep
from server.deps.session_dep import SessionDep
from server.models.database.reservation_db_model import Reservation
from server.models.http.requests.reservation_request_models import (
    ReservationRegister,
    ReservationUpdate,
)
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.reservation_repository import ReservationRepository
from server.services.security.buildings_permission_checker import (
    BuildingPermissionChecker,
)
from server.services.security.classrooms_permission_checker import (
    ClassroomPermissionChecker,
)
from server.utils.enums.actions_enums import BuildingAction, ClassroomAction
from server.utils.must_be_int import must_be_int


class ReservationRespositoryAdapter:
    def __init__(
        self,
        session: SessionDep,
        user: UserDep,
        interval: QueryIntervalDep,
        permission_index: PermissionIndexDep,
        scope: AccessScopeDep,
    ):
        self.session = session
        self.scope = scope
        self.interval = interval
        self.user = user
        self.checker = ClassroomPermissionChecker(
            user=user, session=session, permission_index=permission_index
        )
        self.building_checker = BuildingPermissionChecker(
            user=user, session=session, permission_index=permission_index
        )

    def get_all(self) -> list[Reservation]:
        """Get all reservations for authenticated user on owned buildings"""
        if self.scope.classroom_grant(ClassroomAction.READ).all:
            return ReservationRepository.get_all(
                session=self.session, interval=self.interval
            )
        return ReservationRepository.get_all_on_classrooms(
            classroom_ids=self.scope.classroom_ids(ClassroomAction.READ),
            session=self.session,
            interval=self.interval,
        )

    def get_by_id(
        self, id: int, action: ClassroomAction = ClassroomAction.READ
    ) -> Reservation:
        """Get a reservation by id, checking that the user can do `action` on it
        (READ to show it; RESERVE when it is fetched to be changed, since the
        whole booking lifecycle takes RESERVE, see docs/PERMISSIONS.md).
        - If the reservation has a classroom, check the permission on it.
        - Otherwise check the permission on the building.
        """
        reservation = ReservationRepository.get_by_id(id=id, session=self.session)
        classroom = reservation.get_classroom()
        if classroom:
            self.checker.check_permission(classroom, action)
        if not classroom:
            self.building_checker.check_permission(
                reservation.get_building(), BuildingAction(action.value)
            )
        return reservation

    def create(
        self,
        reservation: ReservationRegister,
    ) -> Reservation:
        classroom = ClassroomRepository.get_by_id(
            id=reservation.classroom_id, session=self.session
        )
        self.checker.check_permission(
            must_be_int(classroom.id), ClassroomAction.RESERVE
        )
        new_reservation = ReservationRepository.create(
            creator=self.user,
            input=reservation,
            classroom=classroom,
            session=self.session,
        )
        self.session.commit()
        self.session.refresh(new_reservation)
        return new_reservation

    def update(
        self,
        id: int,
        input: ReservationUpdate,
    ) -> Reservation:
        classroom = ClassroomRepository.get_by_id(
            id=input.classroom_id, session=self.session
        )
        self.checker.check_permission(
            must_be_int(classroom.id), ClassroomAction.RESERVE
        )
        reservation = ReservationRepository.update(
            id=id,
            input=input,
            classroom=classroom,
            user=self.user,
            session=self.session,
        )
        self.session.commit()
        self.session.refresh(reservation)
        return reservation

    def delete(self, id: int) -> None:
        reservation = ReservationRepository.get_by_id(id=id, session=self.session)
        classroom = reservation.get_classroom()
        if not classroom:
            self.building_checker.check_permission(
                reservation.get_building(), BuildingAction.RESERVE
            )
        if classroom:
            self.checker.check_permission(classroom, ClassroomAction.RESERVE)
        ReservationRepository.delete(
            id=id,
            user=self.user,
            session=self.session,
        )
        self.session.commit()


ReservationRepositoryDep = Annotated[ReservationRespositoryAdapter, Depends()]
