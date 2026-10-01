from sqlmodel import Session

from server.models.database.occurrence_db_model import Occurrence
from server.models.database.user_db_model import User
from server.repositories.occurrence_repository import OccurrenceRepository
from server.services.security.base_permission_checker import PermissionChecker
from server.services.security.classrooms_permission_checker import (
    ClassroomPermissionChecker,
)
from server.services.security.role_permission_evaluator import PermissionIndex
from server.services.security.schedule_permission_checker import (
    SchedulePermissionChecker,
)
from server.utils.enums.actions_enums import ClassroomAction


class OccurrencePermissionChecker(PermissionChecker[Occurrence]):
    def __init__(
        self, user: User, session: Session, permission_index: PermissionIndex
    ) -> None:
        super().__init__(user, session)
        self.classroom_checker = ClassroomPermissionChecker(
            user=user, session=session, permission_index=permission_index
        )
        self.schedule_checker = SchedulePermissionChecker(
            user=user, session=session, permission_index=permission_index
        )

    def check_permission(  # type: ignore[override]
        self,
        object: int | Occurrence | list[int] | list[Occurrence],
        action: ClassroomAction,
    ) -> None:
        """
        Checks the permission of a user for a specific occurrence.

        Parameters:
        - object (int | Occurrence | list[int] | list[Occurrence]): The occurrence ID, occurrence object, list of occurrence IDs, or list of occurrence objects for which the permission needs to be checked.
        - action (ClassroomAction): The action being performed on the occurrence(s).
        """
        if self.user.is_admin:
            return

        if isinstance(object, int):
            self.__occurrence_id_permission_checker(object, action)
        elif isinstance(object, Occurrence):
            self.__occurrence_obj_permission_checker(object, action)
        elif isinstance(object, list):
            self.__occurrence_list_permission_checker(object, action)

    def __occurrence_id_permission_checker(
        self, occurrence_id: int, action: ClassroomAction
    ) -> None:
        occurrence = OccurrenceRepository.get_by_id(
            id=occurrence_id, session=self.session
        )
        self.__occurrence_obj_permission_checker(occurrence, action)

    def __occurrence_obj_permission_checker(
        self, occurrence: Occurrence, action: ClassroomAction
    ) -> None:
        if occurrence.classroom:
            self.classroom_checker.check_permission(occurrence.classroom, action)
        else:
            self.schedule_checker.check_permission(occurrence.schedule, action)

    def __occurrence_list_permission_checker(
        self, occurrences: list[int] | list[Occurrence], action: ClassroomAction
    ) -> None:
        for occurrence in occurrences:
            if isinstance(occurrence, Occurrence):
                self.__occurrence_obj_permission_checker(occurrence, action)
            else:
                self.__occurrence_id_permission_checker(occurrence, action)
