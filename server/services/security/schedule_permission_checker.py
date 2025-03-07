from fastapi import HTTPException, status
from sqlmodel import Session

from server.models.database.schedule_db_model import Schedule
from server.models.database.user_db_model import User
from server.repositories.schedule_repository import ScheduleRepository


def schedule_permission_checker(
    user: User,
    schedule: int | Schedule,
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
        __schedule_obj_permission_checker(user, schedule)
        return


def __schedule_id_permission_checker(
    user: User, schedule_id: int, session: Session
) -> None:
    schedule = ScheduleRepository.get_by_id(id=schedule_id, session=session)
    __schedule_obj_permission_checker(user, schedule)


def __schedule_obj_permission_checker(user: User, schedule: Schedule) -> None:
    if schedule.classroom:
        if user.buildings is None or schedule.classroom.building_id not in [
            building.id for building in user.buildings
        ]:
            raise ForbiddenScheduleAccess(
                "Usuário não tem permissão para acessar a agenda alocada em uma sala"
            )
    else:
        if user.buildings is None:
            raise ForbiddenScheduleAccess(
                f"Usuário não tem permissão para acessar a agenda de ID {schedule.id}"
            )
        user_buildings_ids = set([building.id for building in user.buildings])
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
