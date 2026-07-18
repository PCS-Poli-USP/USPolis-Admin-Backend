from fastapi import HTTPException, status
from sqlmodel import Session

from server.models.database.schedule_db_model import Schedule
from server.models.database.user_db_model import User
from server.repositories.schedule_repository import ScheduleRepository
from server.services.security.base_permission_checker import PermissionChecker
from server.services.security.buildings_permission_checker import (
    BuildingPermissionChecker,
)
from server.services.security.classrooms_permission_checker import (
    ClassroomPermissionChecker,
)
from server.services.security.role_permission_evaluator import PermissionIndex
from server.utils.enums.actions_enums import ClassroomAction
from server.utils.must_be_int import must_be_int


class SchedulePermissionChecker(PermissionChecker[Schedule]):
    """
    Schedule to check permissions for schedules.
    """

    def __init__(
        self, user: User, session: Session, permission_index: PermissionIndex
    ) -> None:
        super().__init__(user=user, session=session)
        self.classroom_checker = ClassroomPermissionChecker(
            user=user, session=session, permission_index=permission_index
        )
        self.building_checker = BuildingPermissionChecker(
            user=user, session=session, permission_index=permission_index
        )

    def check_permission(  # type: ignore[override]
        self,
        object: int | Schedule | list[int] | list[Schedule],
        action: ClassroomAction,
    ) -> None:
        """
        Checks the permission of a user for a specific schedule.

        Parameters:
        - object (int | Schedule | list[int] | list[Schedule]): The schedule ID, Schedule object, list of schedule IDs, or list of schedule objects for which the permission needs to be checked.
        - action (ClassroomAction): The action being performed on the schedule(s).
        """
        if self.user.is_admin:
            return

        if isinstance(object, int):
            self.__schedule_id_permission_checker(object, action)
        elif isinstance(object, Schedule):
            self.__schedule_obj_permission_checker(object, action)
        elif isinstance(object, list):
            self.__schedule_list_permission_checker(object, action)

    def __schedule_list_permission_checker(
        self, schedules: list[int] | list[Schedule], action: ClassroomAction
    ) -> None:
        for schedule in schedules:
            if isinstance(schedule, Schedule):
                self.__schedule_obj_permission_checker(schedule, action)
            else:
                self.__schedule_id_permission_checker(schedule, action)

    def __schedule_id_permission_checker(
        self, schedule_id: int, action: ClassroomAction
    ) -> None:
        schedule = ScheduleRepository.get_by_id(id=schedule_id, session=self.session)
        self.__schedule_obj_permission_checker(schedule, action)

    def __schedule_obj_permission_checker(
        self, schedule: Schedule, action: ClassroomAction
    ) -> None:
        if schedule.classroom:
            self.classroom_checker.check_permission(schedule.classroom, action)
            return

        if schedule.class_:
            buildings_ids = [
                must_be_int(building.id) for building in schedule.class_.subject.buildings
            ]
            if buildings_ids and not any(
                self.building_checker.is_allowed(building_id, action)
                for building_id in buildings_ids
            ):
                raise ForbiddenScheduleAccess(
                    f"Usuário não tem permissão para acessar a agenda de ID {schedule.id}"
                )
        if schedule.reservation:
            building = schedule.reservation.get_building()
            if building and not self.building_checker.is_allowed(
                must_be_int(building.id), action
            ):
                raise ForbiddenScheduleAccess(
                    f"Usuário não tem permissão para acessar a agenda da reserva {schedule.reservation.title}"
                )


class ForbiddenScheduleAccess(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
