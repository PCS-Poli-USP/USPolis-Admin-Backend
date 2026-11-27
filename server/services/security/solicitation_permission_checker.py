from fastapi import HTTPException, status
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
        """Same rule as Solicitation.get_administrative_users: the groups of
        the allocated or solicited classroom, or, with no classroom, only the
        building main group."""
        classroom = solicitation.get_responsible_classroom()
        if classroom is not None:
            allowed = classroom.id in self.user.classrooms_ids_set()
        else:
            main_group_id = solicitation.building.main_group_id
            allowed = (
                main_group_id is not None and main_group_id in self.user.group_ids_set()
            )
        if not allowed:
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
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )
