from typing import Annotated

from fastapi import Depends

from server.deps.authenticate import UserDep
from server.deps.interval_dep import QueryIntervalDep
from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.session_dep import SessionDep
from server.models.database.reservation_db_model import Reservation
from server.models.http.requests.reservation_request_models import (
    ReservationRegister,
    ReservationUpdate,
)
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.reservation_repository import ReservationRepository
from server.services.security.classrooms_permission_checker import (
    ClassroomPermissionChecker,
)
from server.utils.must_be_int import must_be_int


class ReservationRespositoryAdapter:
    def __init__(
        self,
        owned_building_ids: OwnedBuildingIdsDep,
        session: SessionDep,
        user: UserDep,
        interval: QueryIntervalDep,
    ):
        self.session = session
        self.interval = interval
        self.user = user
        self.owned_building_ids = owned_building_ids
        self.checker = ClassroomPermissionChecker(user=user, session=session)

    def get_all(self) -> list[Reservation]:
        """Get all reservations for authenticated user on owned buildings"""
        if self.user.is_admin:
            return ReservationRepository.get_all(
                session=self.session, interval=self.interval
            )
        return ReservationRepository.get_all_on_classrooms(
            classroom_ids=self.user.classrooms_ids(),
            session=self.session,
            interval=self.interval,
        )

    def get_by_id(self, id: int) -> Reservation:
        """Get a reservation by id, checking if the user has permission to access it.
        - If the user is not an admin, check if they have permission on the classroom of reservation.
        """
        reservation = ReservationRepository.get_by_id(id=id, session=self.session)
        self.checker.check_permission(reservation.classroom)
        return reservation

    def create(
        self,
        reservation: ReservationRegister,
    ) -> Reservation:
        classroom = ClassroomRepository.get_by_id(
            id=reservation.classroom_id, session=self.session
        )
        self.checker.check_permission(must_be_int(classroom.id))
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
        self.checker.check_permission(must_be_int(classroom.id))
        reservation = ReservationRepository.update_on_classrooms(
            id=id,
            classroom_ids=self.user.classrooms_ids(),
            input=input,
            classroom=classroom,
            user=self.user,
            session=self.session,
        )
        self.session.commit()
        self.session.refresh(reservation)
        return reservation

    def delete(self, id: int) -> None:
        ReservationRepository.delete_on_buildings(
            id=id,
            building_ids=self.owned_building_ids,
            user=self.user,
            session=self.session,
        )
        self.session.commit()


ReservationRepositoryDep = Annotated[ReservationRespositoryAdapter, Depends()]
