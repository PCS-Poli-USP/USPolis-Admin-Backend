from fastapi import HTTPException, status
from sqlmodel import Session

from server.models.database.occurrence_db_model import Occurrence
from server.models.database.user_db_model import User
from server.repositories.occurrence_repository import OccurrenceRepository
from server.services.security.schedule_permission_checker import (
    schedule_permission_checker,
)


def occurrence_permission_checker(
    user: User,
    occurrence: int | Occurrence,
    session: Session,
) -> None:
    """
    Checks the permission of a user for a specific occurrence.

    Parameters:
    - user (User): The user object for which the permission needs to be checked.
    - occurrence (int | occurrence | list[int] | list[occurrence]): The occurrence ID, occurrence object, list of occurrence IDs, or list of occurrence objects for which the permission needs to be checked.
    - Session: The session of database
    """
    if user.is_admin:
        return

    if isinstance(occurrence, int):
        __occurrence_id_permission_checker(user, occurrence, session)
    elif isinstance(occurrence, Occurrence):
        __occurrence_obj_permission_checker(user, occurrence, session)
        return


def __occurrence_id_permission_checker(
    user: User, occurrence_id: int, session: Session
) -> None:
    occurrence = OccurrenceRepository.get_by_id(id=occurrence_id, session=session)
    __occurrence_obj_permission_checker(user, occurrence, session)


def __occurrence_obj_permission_checker(
    user: User, occurrence: Occurrence, session: Session
) -> None:
    if user.buildings is None:
        raise ForbiddenOccurrenceAccess(
            "Usuário não tem permissão para acessar essa ocorrência"
        )
    if occurrence.classroom:
        if user.buildings is None or occurrence.classroom.building_id not in [
            building.id for building in user.buildings
        ]:
            raise ForbiddenOccurrenceAccess(
                "Usuário não tem permissão para acessar essa ocorrência"
            )
    else:
        schedule = occurrence.schedule
        schedule_permission_checker(user, schedule, session)


class ForbiddenOccurrenceAccess(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
