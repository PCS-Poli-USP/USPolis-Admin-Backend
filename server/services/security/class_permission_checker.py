from fastapi import HTTPException, status
from sqlmodel import Session

from server.models.database.class_db_model import Class
from server.models.database.user_db_model import User
from server.repositories.building_repository import BuildingRepository
from server.repositories.class_repository import ClassRepository


def class_permission_checker(
    user: User,
    class_: int | Class | list[int] | list[Class],
    session: Session,
) -> None:
    """
    Checks the permission of a user for a specific class.

    Parameters:
    - user (User): The user object for which the permission needs to be checked.
    - class_ (int | Class | list[int] | list[Class]): The class ID, class object, list of class IDs, or list of class objects for which the permission needs to be checked.
    - Session: The session of database
    """
    if user.is_admin:
        return

    if isinstance(class_, int):
        __class_id_permission_checker(user, class_, session)
    elif isinstance(class_, Class):
        __class_obj_permission_checker(user, class_, session)
    elif isinstance(class_, list):
        __class_list_permission_checker(user, class_, session)


def __class_id_permission_checker(user: User, class_id: int, session: Session) -> None:
    current = BuildingRepository.get_by_class_id(
        class_id=class_id, session=session)
    if user.buildings is None or current.id not in [
        building.id for building in user.buildings
    ]:
        raise ForbiddenClassAccess([class_id])


def __class_obj_permission_checker(user: User, class_: Class, session: Session) -> None:
    current = BuildingRepository.get_by_class(class_=class_, session=session)
    if user.buildings is None or current not in user.buildings:
        raise ForbiddenClassAccess([class_.id])  # type: ignore


def __class_list_permission_checker(
    user: User, classes: list[int] | list[Class], session: Session
) -> None:
    buildings_ids = [
        BuildingRepository.get_by_class(class_=class_, session=session).id
        if isinstance(class_, Class)
        else BuildingRepository.get_by_class_id(class_id=class_, session=session).id
        for class_ in classes
    ]
    if user.buildings is None or not set(buildings_ids).issubset(
        set([building.id for building in user.buildings])
    ):
        classes_ids: list[int] = []
        for class_ in classes:
            if isinstance(class_, Class):
                if (class_.id):
                    classes_ids.append(class_.id)
            else:
                classes_ids.append(class_)
        raise ForbiddenClassAccess(classes_ids)


class ForbiddenClassAccess(HTTPException):
    def __init__(self, class_ids: list[int]):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User do not have access to class: {class_ids}",
        )
