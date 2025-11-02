from fastapi import HTTPException, status
from sqlmodel import Session
from server.models.database.reservation_db_model import Reservation
from server.models.database.user_db_model import User
from server.repositories.reservation_repository import ReservationRepository
from server.services.security.base_permission_checker import PermissionChecker


class ReservationPermissionChecker(PermissionChecker[Reservation]):
    def __init__(self, user: User, session: Session):
        super().__init__(user=user, session=session)

    def check_permission(
        self, object: int | Reservation | list[int] | list[Reservation]
    ) -> None:
        if self.user.is_admin:
            return

        if isinstance(object, int):
            self.__reservation_id_permission_checker(object)
        elif isinstance(object, Reservation):
            self.__reservation_obj_permission_checker(object)
        elif isinstance(object, list):
            self.__reservation_list_permission_checker(object)

    def __reservation_id_permission_checker(self, reservation_id: int) -> None:
        reservation = ReservationRepository.get_by_id(
            id=reservation_id, session=self.session
        )
        self.__reservation_obj_permission_checker(reservation)

    def __reservation_obj_permission_checker(self, reservation: Reservation) -> None:
        classroom = reservation.get_classroom()
        if classroom and classroom.id not in self.user.classrooms_ids_set():
            raise ForbiddenReservationAccess(
                "Vocẽ não tem permissão para acessar esta reserva."
            )
        if not classroom:
            building = reservation.get_building()
            if building.id not in self.user.buildings_ids_set():
                raise ForbiddenReservationAccess(
                    "Vocẽ não tem permissão para acessar esta reserva."
                )

    def __reservation_list_permission_checker(
        self, reservations: list[int] | list[Reservation]
    ) -> None:
        for reservation in reservations:
            if isinstance(reservation, int):
                self.__reservation_id_permission_checker(reservation)
            elif isinstance(reservation, Reservation):
                self.__reservation_obj_permission_checker(reservation)


class ForbiddenReservationAccess(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )
