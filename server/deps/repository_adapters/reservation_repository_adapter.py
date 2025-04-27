from typing import Annotated

from fastapi import Depends

from server.deps.authenticate import UserDep
from server.deps.owned_building_ids import OwnedBuildingIdsDep
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
from server.utils.must_be_int import must_be_int


class ReservationRespositoryAdapter:
    def __init__(
        self,
        owned_building_ids: OwnedBuildingIdsDep,
        session: SessionDep,
        user: UserDep,
    ):
        self.session = session
        self.user = user
        self.owned_building_ids = owned_building_ids
        self.checker = BuildingPermissionChecker(user=user, session=session)

    def get_all(self) -> list[Reservation]:
        return ReservationRepository.get_all_on_buildings(
            building_ids=self.owned_building_ids, session=self.session
        )

    def get_by_id(self, id: int) -> Reservation:
        reservation = ReservationRepository.get_by_id_on_buildings(
            id=id, building_ids=self.owned_building_ids, session=self.session
        )
        return reservation

    def create(
        self,
        reservation: ReservationRegister,
    ) -> Reservation:
        classroom = ClassroomRepository.get_by_id(
            id=reservation.classroom_id, session=self.session
        )
        self.checker.check_permission(must_be_int(classroom.building_id))
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
        self.checker.check_permission(must_be_int(classroom.building_id))
        reservation = ReservationRepository.update_on_buildings(
            id=id,
            building_ids=self.owned_building_ids,
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
