from fastapi import HTTPException
from sqlmodel import Session

from server.models.database.classroom_solicitation_db_model import ClassroomSolicitation
from server.models.database.user_db_model import User
from server.repositories.classroom_solicitation_repository import (
    ClassroomSolicitationRepository,
)
from server.services.security.base_permission_checker import PermissionChecker


class ClassroomSolicitationPermissionChecker(PermissionChecker[ClassroomSolicitation]):
    """
    Permission checker for ClassroomSolicitation.
    """

    def __init__(self, user: User, session: Session):
        super().__init__(user=user, session=session)

    def check_permission(
        self,
        object: int | ClassroomSolicitation | list[int] | list[ClassroomSolicitation],
    ) -> None:
        if self.user.is_admin:
            return

        if isinstance(object, int):
            self.__solicitation_id_permission_checker(object)
        elif isinstance(object, ClassroomSolicitation):
            self.__solicitation_obj_permission_checker(object)
        elif isinstance(object, list):
            self.__solicitation_list_permission_checker(object)

    def __solicitation_id_permission_checker(self, solicitation_id: int) -> None:
        solicitation = ClassroomSolicitationRepository.get_by_id(
            id=solicitation_id, session=self.session
        )
        self.__solicitation_obj_permission_checker(solicitation)

    def __solicitation_obj_permission_checker(
        self,
        solicitation: ClassroomSolicitation,
    ) -> None:
        user_ids = self.user.classrooms_ids_set()
        if solicitation.classroom_id not in user_ids:
            raise ForbiddenClassroomSolicitationAccess(
                f"Usuário não tem permissão para acessar a solicitação de sala {solicitation.id}"
            )

    def __solicitation_list_permission_checker(
        self,
        solicitations: list[int] | list[ClassroomSolicitation],
    ) -> None:
        for solicitation in solicitations:
            if isinstance(solicitation, ClassroomSolicitation):
                self.__solicitation_obj_permission_checker(solicitation)
            else:
                self.__solicitation_id_permission_checker(solicitation)


class ForbiddenClassroomSolicitationAccess(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=403,
            detail=detail,
        )
