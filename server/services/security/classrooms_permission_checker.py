from fastapi import HTTPException
from sqlmodel import Session

from server.models.database.classroom_db_model import Classroom
from server.models.database.user_db_model import User
from server.services.security.base_permission_checker import PermissionChecker
from server.utils.must_be_int import must_be_int


class ClassroomPermissionChecker(PermissionChecker[Classroom]):
    def __init__(self, user: User, session: Session) -> None:
        super().__init__(user=user, session=session)

    def check_permission(
        self, object: int | Classroom | list[int] | list[Classroom]
    ) -> None:
        """
        Checks the permission of a user for a specific classroom.

        Parameters:
        - user (User): The user object for which the permission needs to be checked.
        - classroom (int | Classroom | list[int] | list[Classroom]): The classroom ID, Classroom object, list of classroom IDs, or list of Classroom objects for which the permission needs to be checked.
        """
        if self.user.is_admin:
            return

        if isinstance(object, int):
            self.__classroom_id_permission_checker(object)
        elif isinstance(object, Classroom):
            self.__classroom_obj_permission_checker(object)
        elif isinstance(object, list):
            self.__classroom_list_permission_checker(object)

    def __classroom_id_permission_checker(
        self,
        classroom_id: int,
    ) -> None:
        user_ids = self.user.classrooms_ids_set()
        if classroom_id not in user_ids:
            raise ForbiddenClassroomAccess(
                "Usuário não tem permissão para acessar a sala"
            )

    def __classroom_obj_permission_checker(self, classroom: Classroom) -> None:
        user_ids = self.user.classrooms_ids_set()
        if must_be_int(classroom.id) not in user_ids:
            raise ForbiddenClassroomAccess(
                "Usuário não tem permissão para acessar a sala"
            )

    def __classroom_list_permission_checker(
        self,
        classrooms: list[int] | list[Classroom],
    ) -> None:
        classrooms_ids = [
            must_be_int(classroom.id) if isinstance(classroom, Classroom) else classroom
            for classroom in classrooms
        ]
        user_ids = self.user.classrooms_ids_set()
        if not set(classrooms_ids).issubset(user_ids):
            raise ForbiddenClassroomAccess(
                "Usuário não tem permissão para acessar uma ou mais salas"
            )


class ForbiddenClassroomAccess(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=403,
            detail=detail,
        )
