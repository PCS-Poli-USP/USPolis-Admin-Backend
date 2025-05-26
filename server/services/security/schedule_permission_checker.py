from fastapi import HTTPException, status
from sqlmodel import Session

from server.models.database.schedule_db_model import Schedule
from server.models.database.user_db_model import User
from server.repositories.schedule_repository import ScheduleRepository
from server.services.security.base_permission_checker import PermissionChecker


class SchedulePermissionChecker(PermissionChecker[Schedule]):
    """
    Schedule to check permissions for schedules.
    """

    def __init__(self, user: User, session: Session) -> None:
        super().__init__(user=user, session=session)

    def check_permission(
        self,
        object: int | Schedule | list[int] | list[Schedule],
    ) -> None:
        """
        Checks the permission of a user for a specific schedule.

        Parameters:
        - user (User): The user object for which the permission needs to be checked.
        - schedule (int | Schedule | list[int] | list[Schedule]): The schedule ID, Schedule object, list of schedule IDs, or list of schedule objects for which the permission needs to be checked.
        """
        if self.user.is_admin:
            return

        if isinstance(object, int):
            self.__schedule_id_permission_checker(object)
        elif isinstance(object, Schedule):
            self.__schedule_obj_permission_checker(object)
        elif isinstance(object, list):
            self.__schedule_list_permission_checker(object)

    def __schedule_list_permission_checker(
        self,
        schedules: list[int] | list[Schedule],
    ) -> None:
        for schedule in schedules:
            if isinstance(schedule, Schedule):
                self.__schedule_obj_permission_checker(schedule)
            else:
                self.__schedule_id_permission_checker(schedule)

    def __schedule_id_permission_checker(self, schedule_id: int) -> None:
        schedule = ScheduleRepository.get_by_id(id=schedule_id, session=self.session)
        self.__schedule_obj_permission_checker(schedule)

    def __schedule_obj_permission_checker(self, schedule: Schedule) -> None:
        if schedule.classroom:
            user_ids = self.user.classrooms_ids_set()
            if schedule.classroom_id not in user_ids:
                raise ForbiddenScheduleAccess(
                    f"Usuário não tem permissão para acessar a agenda da sala {schedule.classroom_id}"
                )
        else:
            if self.user.buildings is None:
                raise ForbiddenScheduleAccess(
                    f"Usuário não tem permissão para acessar a agenda de ID {schedule.id}"
                )
            user_buildings_ids = self.user.buildings_ids_set()
            if schedule.class_:
                buildings_ids = [
                    building.id for building in schedule.class_.subject.buildings
                ]
                if len(set(buildings_ids).intersection(user_buildings_ids)) == 0:
                    raise ForbiddenScheduleAccess(
                        f"Usuário não tem permissão para acessar a agenda de ID {schedule.id}"
                    )
            if schedule.reservation:
                buildings_ids = [schedule.reservation.classroom.building_id]
                if len(set(buildings_ids).intersection(user_buildings_ids)) == 0:
                    raise ForbiddenScheduleAccess(
                        f"Usuário não tem permissão para acessar a agenda da reserva {schedule.reservation.title}"
                    )


class ForbiddenScheduleAccess(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
