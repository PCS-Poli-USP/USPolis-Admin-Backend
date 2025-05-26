from fastapi import HTTPException, status
from sqlmodel import Session

from server.models.database.occurrence_db_model import Occurrence
from server.models.database.user_db_model import User
from server.repositories.occurrence_repository import OccurrenceRepository
from server.services.security.base_permission_checker import PermissionChecker
from server.services.security.schedule_permission_checker import (
    SchedulePermissionChecker,
)


class OccurrencePermissionChecker(PermissionChecker[Occurrence]):
    def __init__(self, user: User, session: Session) -> None:
        super().__init__(user, session)
        self.schedule_checker = SchedulePermissionChecker(user=user, session=session)

    def check_permission(
        self,
        object: int | Occurrence | list[int] | list[Occurrence],
    ) -> None:
        """
        Checks the permission of a user for a specific occurrence.

        Parameters:
        - user (User): The user object for which the permission needs to be checked.
        - occurrence (int | Occurrence | list[int] | list[Occurrence]): The occurrence ID, occurrence object, list of occurrence IDs, or list of occurrence objects for which the permission needs to be checked.
        """
        if self.user.is_admin:
            return

        if isinstance(object, int):
            self.__occurrence_id_permission_checker(object)
        elif isinstance(object, Occurrence):
            self.__occurrence_obj_permission_checker(object)
        elif isinstance(object, list):
            self.__occurrence_list_permission_checker(object)

    def __occurrence_id_permission_checker(self, occurrence_id: int) -> None:
        occurrence = OccurrenceRepository.get_by_id(
            id=occurrence_id, session=self.session
        )
        self.__occurrence_obj_permission_checker(occurrence)

    def __occurrence_obj_permission_checker(self, occurrence: Occurrence) -> None:
        if occurrence.classroom:
            classroom_id = occurrence.classroom_id
            if classroom_id not in self.user.classrooms_ids_set():
                raise ForbiddenOccurrenceAccess(
                    f"Usuário não tem permissão para acessar a ocorrência {occurrence.id}"
                )
        else:
            schedule = occurrence.schedule
            self.schedule_checker.check_permission(schedule)

    def __occurrence_list_permission_checker(
        self,
        occurrences: list[int] | list[Occurrence],
    ) -> None:
        for occurrence in occurrences:
            if isinstance(occurrence, Occurrence):
                self.__occurrence_obj_permission_checker(occurrence)
            else:
                self.__occurrence_id_permission_checker(occurrence)


class ForbiddenOccurrenceAccess(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
