from fastapi import HTTPException, status
from sqlmodel import Session

from server.models.database.group_db_model import Group
from server.models.database.user_db_model import User
from server.services.security.base_permission_checker import PermissionChecker
from server.utils.must_be_int import must_be_int


class GroupPermissionChecker(PermissionChecker[Group]):
    def __init__(self, user: User, session: Session) -> None:
        super().__init__(user=user, session=session)

    def check_permission(self, object: int | Group | list[int] | list[Group]) -> None:
        """
        Checks the permission of a user for a specific classroom.

        Parameters:
        - user (User): The user object for which the permission needs to be checked.
        - classroom (int | Classroom | list[int] | list[Classroom]): The classroom ID, Classroom object, list of classroom IDs, or list of Classroom objects for which the permission needs to be checked.
        """
        if self.user.is_admin:
            return

        if isinstance(object, int):
            self.__group_id_permission_checker(object)
        elif isinstance(object, Group):
            self.__group_obj_permission_checker(object)
        elif isinstance(object, list):
            self.__group_list_permission_checker(object)

    def __group_id_permission_checker(
        self,
        group_id: int,
    ) -> None:
        user_ids = self.user.classrooms_ids_set()
        if group_id not in user_ids:
            raise ForbiddenGroupAccess()

    def __group_obj_permission_checker(self, group: Group) -> None:
        user_ids = self.user.group_ids()
        if must_be_int(group.id) not in user_ids:
            raise ForbiddenGroupAccess()

    def __group_list_permission_checker(
        self,
        groups: list[int] | list[Group],
    ) -> None:
        group_ids = [
            must_be_int(group.id) if isinstance(group, Group) else group
            for group in groups
        ]
        user_ids = self.user.group_ids_set()
        if not set(group_ids).issubset(user_ids):
            raise ForbiddenGroupAccess()


class ForbiddenGroupAccess(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não tem permissão para acessar essa grupo",
        )
