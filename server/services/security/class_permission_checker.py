from fastapi import HTTPException, status
from sqlmodel import Session

from server.models.database.class_db_model import Class
from server.models.database.user_db_model import User
from server.repositories.class_repository import ClassRepository
from server.services.security.access_scope import AccessScope
from server.services.security.base_permission_checker import PermissionChecker
from server.services.security.buildings_permission_checker import (
    BuildingPermissionChecker,
)
from server.services.security.classrooms_permission_checker import (
    ClassroomPermissionChecker,
)
from server.services.security.role_permission_evaluator import PermissionIndex
from server.utils.enums.actions_enums import ClassroomAction, translate_action


class ClassPermissionChecker(PermissionChecker[Class]):
    """
    Class to check permissions for classes.
    """

    def __init__(
        self, user: User, session: Session, permission_index: PermissionIndex
    ) -> None:
        super().__init__(user=user, session=session)
        self.building_checker = BuildingPermissionChecker(
            user=user, session=session, permission_index=permission_index
        )
        self.classroom_checker = ClassroomPermissionChecker(
            user=user, session=session, permission_index=permission_index
        )
        self.scope = AccessScope(
            user=user, session=session, permission_index=permission_index
        )

    def check_permission(  # type: ignore[override]
        self,
        object: int | Class | list[int] | list[Class],
        action: ClassroomAction,
    ) -> None:
        """
        Checks the permission of a user for a specific class. **A user can do `action` on a class if:**
        - The user is an admin.
        - At least one of its schedules is allocated in a classroom where the user can do `action` (a classroom grant is enough, no building grant needed).
        - Or at least one of its schedules is unallocated and the user can do `action` on one of the class's buildings.

        **IMPORTANT:** This method not check a strict permission, so if one of the schedules of the class is allocated in a classroom that the user has access to, the user will be allowed to access the class. For deleting a class you should check if the user has access to all schedules of the class.

        Parameters:
        - user (User): The user object for which the permission needs to be checked.
        - class_ (int | Class | list[int] | list[Class]): The class ID, class object, list of class IDs, or list of class objects for which the permission needs to be checked.
        - action (ClassroomAction): The action being performed on the class(es).
        """
        if self.user.is_admin:
            return

        if isinstance(object, int):
            self.__class_id_permission_checker(object, action)
        elif isinstance(object, Class):
            self.__class_obj_permission_checker(object, action)
        elif isinstance(object, list):
            self.__class_list_permission_checker(object, action)

    def __class_id_permission_checker(
        self, class_id: int, action: ClassroomAction
    ) -> None:
        class_ = ClassRepository.get_by_id(id=class_id, session=self.session)
        self.__class_obj_permission_checker(class_, action)

    def __class_obj_permission_checker(
        self, class_: Class, action: ClassroomAction
    ) -> None:
        # Reading: whoever belongs to one of the subject's buildings (can read
        # the building or any classroom in it) reads every class of the
        # subject, allocated or not, wherever its schedules are. Same rule as
        # the listings (AccessScope.readable_building_ids), see
        # docs/PERMISSIONS.md, "Class visibility".
        if action == ClassroomAction.READ and self.__in_a_readable_building(
            class_.building_ids()
        ):
            return

        # Everything else goes through the schedules:
        # - an allocated schedule, through its classroom: the action on that
        #   classroom is enough (a classroom-level role manages the classes
        #   allocated in its classrooms, without any grant on the building);
        # - an unallocated schedule, through the class's buildings.
        allowed = any(
            self.classroom_checker.is_allowed(schedule.classroom_id, action)
            for schedule in class_.schedules
            if schedule.classroom_id
        )
        if not allowed and any(
            not schedule.classroom_id for schedule in class_.schedules
        ):
            allowed = any(
                self.building_checker.is_allowed(building_id, action)
                for building_id in class_.building_ids()
            )

        if not allowed:
            raise ForbiddenClassAccess(
                f"Usuário não tem permissão para {translate_action(action)} "
                f"a turma {class_.subject.code} - {class_.code}"
            )

    def __in_a_readable_building(self, building_ids: set[int]) -> bool:
        readable = self.scope.visible_building_grant(ClassroomAction.READ)
        return readable.all or bool(readable.ids & building_ids)

    def __class_list_permission_checker(
        self, classes: list[int] | list[Class], action: ClassroomAction
    ) -> None:
        for class_ in classes:
            if isinstance(class_, Class):
                self.__class_obj_permission_checker(class_, action)
            else:
                self.__class_id_permission_checker(class_, action)


class ForbiddenClassAccess(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )
