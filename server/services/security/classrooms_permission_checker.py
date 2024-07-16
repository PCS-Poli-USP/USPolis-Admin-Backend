from fastapi import HTTPException, status
from sqlmodel import Session

from server.models.database.classroom_db_model import Classroom
from server.models.database.user_db_model import User
from server.repositories.classroom_repository import ClassroomRepository


def classroom_permission_checker(
    user: User,
    classroom: int | Classroom | list[int] | list[Classroom],
    session: Session,
) -> None:
    """
    Checks the permission of a user for a specific classroom.

    Parameters:
    - user (User): The user object for which the permission needs to be checked.
    - classroom (int | Classroom | list[int] | list[Classroom]): The classroom ID, Classroom object, list of classroom IDs, or list of classroom objects for which the permission needs to be checked.
    - Session: The session of database
    """
    if user.is_admin:
        return

    if isinstance(classroom, int):
        __classroom_id_permission_checker(user, classroom, session)
    elif isinstance(classroom, Classroom):
        __classroom_obj_permission_checker(user, classroom)
    elif isinstance(classroom, list):
        __classroom_list_permission_checker(user, classroom, session)


def __classroom_id_permission_checker(
    user: User, classroom_id: int, session: Session
) -> None:
    classroom = ClassroomRepository.get_by_id(id=classroom_id, session=session)
    if user.buildings is None or classroom.building_id not in [
        building.id for building in user.buildings
    ]:
        raise ForbiddenClassroomAccess([classroom_id])


def __classroom_obj_permission_checker(user: User, classroom: Classroom) -> None:
    if user.buildings is None or classroom.building not in user.buildings:
        raise ForbiddenClassroomAccess([classroom.id])  # type: ignore


def __classroom_list_permission_checker(
    user: User, classrooms: list[int] | list[Classroom], session: Session
) -> None:
    buildings_ids = [
        classroom.building_id
        if isinstance(classroom, Classroom)
        else ClassroomRepository.get_by_id(id=classroom, session=session).building_id
        for classroom in classrooms
    ]
    if user.buildings is None or not set(buildings_ids).issubset(
        set([building.id for building in user.buildings])
    ):
        raise ForbiddenClassroomAccess(classroom_ids)  # type: ignore


class ForbiddenClassroomAccess(HTTPException):
    def __init__(self, classroom_ids: list[int]):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User do not have access to classrooms: {classroom_ids}",
        )
