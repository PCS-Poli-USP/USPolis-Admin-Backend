from sqlmodel import Session
from server.models.database.reservation_db_model import Reservation
from server.models.database.user_db_model import User
from server.repositories.reservation_repository import ReservationRepository
from server.services.security.base_permission_checker import PermissionChecker
from server.services.security.buildings_permission_checker import (
    BuildingPermissionChecker,
)
from server.services.security.classrooms_permission_checker import (
    ClassroomPermissionChecker,
)
from server.services.security.role_permission_evaluator import PermissionIndex
from server.utils.enums.actions_enums import ClassroomAction


class ReservationPermissionChecker(PermissionChecker[Reservation]):
    def __init__(
        self, user: User, session: Session, permission_index: PermissionIndex
    ):
        super().__init__(user=user, session=session)
        self.classroom_checker = ClassroomPermissionChecker(
            user=user, session=session, permission_index=permission_index
        )
        self.building_checker = BuildingPermissionChecker(
            user=user, session=session, permission_index=permission_index
        )

    def check_permission(  # type: ignore[override]
        self,
        object: int | Reservation | list[int] | list[Reservation],
        action: ClassroomAction,
    ) -> None:
        if self.user.is_admin:
            return

        if isinstance(object, int):
            self.__reservation_id_permission_checker(object, action)
        elif isinstance(object, Reservation):
            self.__reservation_obj_permission_checker(object, action)
        elif isinstance(object, list):
            self.__reservation_list_permission_checker(object, action)

    def __reservation_id_permission_checker(
        self, reservation_id: int, action: ClassroomAction
    ) -> None:
        reservation = ReservationRepository.get_by_id(
            id=reservation_id, session=self.session
        )
        self.__reservation_obj_permission_checker(reservation, action)

    def __reservation_obj_permission_checker(
        self, reservation: Reservation, action: ClassroomAction
    ) -> None:
        classroom = reservation.get_classroom()
        if classroom:
            self.classroom_checker.check_permission(classroom, action)
        else:
            self.building_checker.check_permission(reservation.get_building(), action)

    def __reservation_list_permission_checker(
        self, reservations: list[int] | list[Reservation], action: ClassroomAction
    ) -> None:
        for reservation in reservations:
            if isinstance(reservation, int):
                self.__reservation_id_permission_checker(reservation, action)
            elif isinstance(reservation, Reservation):
                self.__reservation_obj_permission_checker(reservation, action)
