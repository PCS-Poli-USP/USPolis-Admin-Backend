from fastapi import HTTPException, status
from sqlmodel import Session

from server.models.database.classroom_db_model import Classroom
from server.models.database.user_db_model import User
from server.services.security.base_permission_checker import PermissionChecker
from server.services.security.role_permission_evaluator import PermissionIndex
from server.utils.enums.actions_enums import ClassroomAction
from server.utils.must_be_int import must_be_int


class ClassroomPermissionChecker(PermissionChecker[Classroom]):
    def __init__(
        self, user: User, session: Session, permission_index: PermissionIndex
    ) -> None:
        super().__init__(user=user, session=session)
        self.permission_index = permission_index

    def check_permission(  # type: ignore[override]
        self,
        object: int | Classroom | list[int] | list[Classroom],
        action: ClassroomAction,
    ) -> None:
        """
        Checks the permission of a user for a specific classroom.

        Parameters:
        - object (int | Classroom | list[int] | list[Classroom]): The classroom ID, Classroom object, list of classroom IDs, or list of Classroom objects for which the permission needs to be checked.
        - action (ClassroomAction): The action being performed on the classroom(s).
        """
        if self.user.is_admin:
            return

        if isinstance(object, int):
            self.__classroom_id_permission_checker(object, action)
        elif isinstance(object, Classroom):
            self.__classroom_obj_permission_checker(object, action)
        elif isinstance(object, list):
            self.__classroom_list_permission_checker(object, action)

    def __building_id_for(self, classroom_id: int) -> int | None:
        classroom = self.session.get(Classroom, classroom_id)
        return classroom.building_id if classroom else None

    def is_allowed(
        self,
        classroom_id: int,
        action: ClassroomAction,
        building_id: int | None = None,
    ) -> bool:
        """Non-raising version of check_permission, for callers that need to test
        several classrooms and decide what to do themselves (e.g. "any of these").
        `building_id` is an optional pre-known hint to skip the cascade's lazy lookup."""
        if classroom_id in self.user.classrooms_ids_set():
            return True
        # Only resolve the classroom's building lazily, since the group-based
        # check above already covers every case until roles have real data.
        if building_id is None:
            building_id = self.__building_id_for(classroom_id)
        return self.permission_index.has_classroom_permission(
            action=action, classroom_id=classroom_id, building_id=building_id
        )

    def __classroom_id_permission_checker(
        self, classroom_id: int, action: ClassroomAction
    ) -> None:
        if not self.is_allowed(classroom_id, action):
            raise ForbiddenClassroomAccess(
                "Usuário não tem permissão para acessar a sala"
            )

    def __classroom_obj_permission_checker(
        self, classroom: Classroom, action: ClassroomAction
    ) -> None:
        classroom_id = must_be_int(classroom.id)
        if not self.is_allowed(classroom_id, action, building_id=classroom.building_id):
            raise ForbiddenClassroomAccess(
                "Usuário não tem permissão para acessar a sala"
            )

    def __classroom_list_permission_checker(
        self, classrooms: list[int] | list[Classroom], action: ClassroomAction
    ) -> None:
        disallowed = [
            classroom
            for classroom in classrooms
            if not self.is_allowed(
                must_be_int(classroom.id) if isinstance(classroom, Classroom) else classroom,
                action,
                building_id=classroom.building_id
                if isinstance(classroom, Classroom)
                else None,
            )
        ]
        if disallowed:
            raise ForbiddenClassroomAccess(
                "Usuário não tem permissão para acessar uma ou mais salas"
            )


class ForbiddenClassroomAccess(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )
