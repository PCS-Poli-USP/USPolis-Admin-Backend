from fastapi import HTTPException, status
from sqlmodel import Session

from server.models.database.class_db_model import Class
from server.models.database.user_db_model import User
from server.repositories.building_repository import BuildingRepository
from server.utils.must_be_int import must_be_int


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
    if user.buildings is None:
        raise ForbiddenClassAccess([class_id])

    buildings = BuildingRepository.get_by_class_id(class_id=class_id, session=session)
    buildings_ids = [must_be_int(building.id) for building in buildings]
    buildings_set = set(buildings_ids)
    users_set = set([building.id for building in user.buildings])
    if len(buildings_set.intersection(users_set)) == 0:
        raise ForbiddenClassAccess([class_id])


def __class_obj_permission_checker(user: User, class_: Class, session: Session) -> None:
    if user.buildings is None:
        raise ForbiddenClassAccess([class_.id])  # type: ignore
    buildings = BuildingRepository.get_by_class(class_=class_, session=session)
    buildings_ids = [must_be_int(building.id) for building in buildings]
    buildings_set = set(buildings_ids)
    users_set = set([building.id for building in user.buildings])
    if len(buildings_set.intersection(users_set)) == 0:
        raise ForbiddenClassAccess([class_.id])  # type: ignore


def __class_list_permission_checker(
    user: User, classes: list[int] | list[Class], session: Session
) -> None:
    buildings_ids: list[int] = []
    for class_ in classes:
        if isinstance(class_, Class):
            buildings = BuildingRepository.get_by_class(class_=class_, session=session)
            buildings_ids.extend([must_be_int(building.id) for building in buildings])
        else:
            buildings = BuildingRepository.get_by_class_id(
                class_id=class_, session=session
            )
            buildings_ids.extend([must_be_int(building.id) for building in buildings])

    if (
        user.buildings is None
        or len(
            set(buildings_ids).intersection(
                set([building.id for building in user.buildings])
            )
        )
        == 0
    ):
        classes_ids: list[int] = []
        for class_ in classes:
            if isinstance(class_, Class):
                if class_.id:
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
