from sqlmodel import Session

from server.models.database.solicitation_db_model import (
    Solicitation,
)
from server.models.database.user_db_model import User
from server.repositories.solicitation_repository import (
    SolicitationRepository,
)
from server.services.security.base_permission_checker import PermissionChecker
from server.services.security.buildings_permission_checker import (
    BuildingPermissionChecker,
)
from server.services.security.classrooms_permission_checker import (
    ClassroomPermissionChecker,
)
from server.services.security.role_permission_evaluator import PermissionIndex
from server.utils.enums.actions_enums import ClassroomAction


class SolicitationPermissionChecker(PermissionChecker[Solicitation]):
    """
    Permission checker for Solicitation.
    """

    def __init__(self, user: User, session: Session, permission_index: PermissionIndex):
        super().__init__(user=user, session=session)
        self.classroom_checker = ClassroomPermissionChecker(
            user=user, session=session, permission_index=permission_index
        )
        self.building_checker = BuildingPermissionChecker(
            user=user, session=session, permission_index=permission_index
        )

    def check_permission(  # type: ignore[override]
        self,
        object: int | Solicitation | list[int] | list[Solicitation],
        action: ClassroomAction,
    ) -> None:
        if self.user.is_admin:
            return

        if isinstance(object, int):
            self.__solicitation_id_permission_checker(object, action)
        elif isinstance(object, Solicitation):
            self.__solicitation_obj_permission_checker(object, action)
        elif isinstance(object, list):
            self.__solicitation_list_permission_checker(object, action)

    def __solicitation_id_permission_checker(
        self, solicitation_id: int, action: ClassroomAction
    ) -> None:
        solicitation = SolicitationRepository.get_by_id(
            id=solicitation_id, session=self.session
        )
        self.__solicitation_obj_permission_checker(solicitation, action)

    def __solicitation_obj_permission_checker(
        self,
        solicitation: Solicitation,
        action: ClassroomAction,
    ) -> None:
        classroom = solicitation.reservation.get_classroom()
        if classroom:
            self.classroom_checker.check_permission(classroom, action)
            return
        building = solicitation.building
        if building:
            self.building_checker.check_permission(building, action)

    def __solicitation_list_permission_checker(
        self,
        solicitations: list[int] | list[Solicitation],
        action: ClassroomAction,
    ) -> None:
        for solicitation in solicitations:
            if isinstance(solicitation, Solicitation):
                self.__solicitation_obj_permission_checker(solicitation, action)
            else:
                self.__solicitation_id_permission_checker(solicitation, action)
