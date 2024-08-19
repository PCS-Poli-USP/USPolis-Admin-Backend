from fastapi import HTTPException, status
from sqlmodel import Session

from server.models.database.schedule_db_model import Schedule
from server.models.database.user_db_model import User
from server.repositories.schedule_repository import ScheduleRepository


def schedule_permission_checker(
    user: User,
    schedule: int | Schedule | list[int] | list[Schedule],
    session: Session,
) -> None:
    """
    Checks the permission of a user for a specific schedule.

    Parameters:
    - user (User): The user object for which the permission needs to be checked.
    - schedule (int | Schedule | list[int] | list[Schedule]): The schedule ID, Schedule object, list of schedule IDs, or list of schedule objects for which the permission needs to be checked.
    - Session: The session of database
    """
    if user.is_admin:
        return

    if isinstance(schedule, int):
        __schedule_id_permission_checker(user, schedule, session)
    elif isinstance(schedule, Schedule):
        # __classroom_obj_permission_checker(user, schedule) TODO
        return
    elif isinstance(schedule, list):
        # __classroom_list_permission_checker(user, schedule, session) TODO
        return


def __schedule_id_permission_checker(
    user: User, schedule_id: int, session: Session
) -> None:
    schedule = ScheduleRepository.get_by_id(id=schedule_id, session=session)
    if schedule.classroom:
        if user.buildings is None or schedule.classroom.building_id not in [
            building.id for building in user.buildings
        ]:
            raise ForbiddenScheduleAccess([schedule_id])
    else:
        if user.buildings is None:
            raise ForbiddenScheduleAccess([schedule_id])
        user_buildings_ids = set([building.id for building in user.buildings])
        if schedule.class_:
            buildings_ids = [
                building.id for building in schedule.class_.subject.buildings
            ]
            if not set(buildings_ids).issubset(user_buildings_ids):
                raise ForbiddenScheduleAccess([schedule_id])
        if schedule.reservation:
            buildings_ids = [schedule.reservation.classroom.building_id]
            if not set(buildings_ids).issubset(user_buildings_ids):
                raise ForbiddenScheduleAccess([schedule_id])


class ForbiddenScheduleAccess(HTTPException):
    def __init__(self, schedule_ids: list[int]):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User do not have access to schedules: {schedule_ids}",
        )
