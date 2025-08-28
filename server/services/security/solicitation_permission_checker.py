from fastapi import HTTPException
from sqlmodel import Session

from server.models.database.solicitation_db_model import (
    Solicitation,
)
from server.models.database.user_db_model import User
from server.repositories.solicitation_repository import (
    SolicitationRepository,
)
from server.services.security.base_permission_checker import PermissionChecker


class SolicitationPermissionChecker(PermissionChecker[Solicitation]):
    """
    Permission checker for Solicitation.
    """

    def __init__(self, user: User, session: Session):
        super().__init__(user=user, session=session)

    def check_permission(
        self,
        object: int | Solicitation | list[int] | list[Solicitation],
    ) -> None:
        if self.user.is_admin:
            return

        if isinstance(object, int):
            self.__solicitation_id_permission_checker(object)
        elif isinstance(object, Solicitation):
            self.__solicitation_obj_permission_checker(object)
        elif isinstance(object, list):
            self.__solicitation_list_permission_checker(object)

    def __solicitation_id_permission_checker(self, solicitation_id: int) -> None:
        solicitation = SolicitationRepository.get_by_id(
            id=solicitation_id, session=self.session
        )
        self.__solicitation_obj_permission_checker(solicitation)

    def __solicitation_obj_permission_checker(
        self,
        solicitation: Solicitation,
    ) -> None:
        classroom = solicitation.reservation.get_classroom()
        user_classrooms_ids = self.user.classrooms_ids_set()
        if classroom and classroom.id not in user_classrooms_ids:
            raise ForbiddenSolicitationAccess(
                f"Usuário não tem permissão para acessar a solicitação de sala {solicitation.reservation.title}"
            )
        if not classroom:
            building = solicitation.building
            user_buildings_ids = self.user.buildings_ids_set()
            if building and building.id not in user_buildings_ids:
                raise ForbiddenSolicitationAccess(
                    f"Usuário não tem permissão para acessar a solicitação de sala {solicitation.reservation.title}"
                )

    def __solicitation_list_permission_checker(
        self,
        solicitations: list[int] | list[Solicitation],
    ) -> None:
        for solicitation in solicitations:
            if isinstance(solicitation, Solicitation):
                self.__solicitation_obj_permission_checker(solicitation)
            else:
                self.__solicitation_id_permission_checker(solicitation)


class ForbiddenSolicitationAccess(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=403,
            detail=detail,
        )
