from fastapi import HTTPException, status
from sqlmodel import Session

from server.models.database.class_db_model import Class
from server.models.database.user_db_model import User
from server.repositories.class_repository import ClassRepository
from server.services.security.base_permission_checker import PermissionChecker


class ClassPermissionChecker(PermissionChecker[Class]):
    """
    Class to check permissions for classes.
    """

    def __init__(self, user: User, session: Session) -> None:
        super().__init__(user=user, session=session)

    def check_permission(self, object: int | Class | list[int] | list[Class]) -> None:
        """
        Checks the permission of a user for a specific class.

        Parameters:
        - user (User): The user object for which the permission needs to be checked.
        - class_ (int | Class | list[int] | list[Class]): The class ID, class object, list of class IDs, or list of class objects for which the permission needs to be checked.
        """
        if self.user.is_admin:
            return

        if isinstance(object, int):
            self.__class_id_permission_checker(object)
        elif isinstance(object, Class):
            self.__class_obj_permission_checker(object)
        elif isinstance(object, list):
            self.__class_list_permission_checker(object)

    def __class_id_permission_checker(self, class_id: int) -> None:
        class_ = ClassRepository.get_by_id(id=class_id, session=self.session)
        self.__class_obj_permission_checker(class_)

    def __class_obj_permission_checker(self, class_: Class) -> None:
        ids = class_.classroom_ids()
        if len(ids.intersection(self.user.classrooms_ids_set())) == 0:
            raise ForbiddenClassAccess(
                f"Usuário não tem permissão para acessar a turma {class_.subject.code} -{class_.code}"
            )

    def __class_list_permission_checker(self, classes: list[int] | list[Class]) -> None:
        for class_ in classes:
            if isinstance(class_, Class):
                self.__class_obj_permission_checker(class_)
            else:
                self.__class_id_permission_checker(class_)


class ForbiddenClassAccess(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )
