from fastapi import HTTPException
from sqlmodel import Session

from server.models.database.classroom_solicitation_db_model import ClassroomSolicitation
from server.models.database.user_db_model import User
from server.repositories.classroom_solicitation_repository import (
    ClassroomSolicitationRepository,
)


def classroom_solicitation_permission_checker(
    user: User,
    solicitation: int | ClassroomSolicitation | list[int] | list[ClassroomSolicitation],
    session: Session,
) -> None:
    """
    Checks the permission of a user for a specific classroom solicitation.

    Parameters:
    - user (User): The user object for which the permission needs to be checked.
    - solicitation (int | ClassroomSolicitation | list[int] | list[ClassroomSolicitation]): The solicitation ID, ClassroomSolicitation object, list of solicitation IDs, or list of ClassroomSolicitation objects for which the permission needs to be checked.
    - Session: The session of database
    """
    if user.is_admin:
        return

    if isinstance(solicitation, int):
        __solicitation_id_permission_checker(user, solicitation, session)
    elif isinstance(solicitation, ClassroomSolicitation):
        __solicitation_obj_permission_checker(user, solicitation)
    elif isinstance(solicitation, list):
        __solicitation_list_permission_checker(user, solicitation, session)


def __solicitation_id_permission_checker(
    user: User, solicitation_id: int, session: Session
) -> None:
    solicitation = ClassroomSolicitationRepository.get_by_id(
        id=solicitation_id, session=session
    )
    if user.buildings is None or solicitation.building.id not in [
        building.id for building in user.buildings
    ]:
        raise ForbiddenClassroomSolicitationAccess(
            "Usuário não tem permissão para acessar a solicitação de sala"
        )


def __solicitation_obj_permission_checker(
    user: User, solicitation: ClassroomSolicitation
) -> None:
    if user.buildings is None or solicitation.building not in user.buildings:
        raise ForbiddenClassroomSolicitationAccess(
            "Usuário não tem permissão para acessar a solicitação de sala"
        )


def __solicitation_list_permission_checker(
    user: User, solicitations: list[int] | list[ClassroomSolicitation], session: Session
) -> None:
    building_ids = [
        solicitation.building.id
        if isinstance(solicitation, ClassroomSolicitation)
        else ClassroomSolicitationRepository.get_by_id(
            id=solicitation, session=session
        ).building.id
        for solicitation in solicitations
    ]
    if user.buildings is None or not set(building_ids).issubset(
        set([building.id for building in user.buildings])
    ):
        raise ForbiddenClassroomSolicitationAccess(
            "Usuário não tem permissão para acessar uma ou mais solicitações de sala"
        )


class ForbiddenClassroomSolicitationAccess(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=403,
            detail=detail,
        )
