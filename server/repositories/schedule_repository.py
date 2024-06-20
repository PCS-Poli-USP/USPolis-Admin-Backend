from fastapi import HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, col, select

from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.schedule_db_model import Schedule
from server.models.http.requests.occurrence_request_models import OccurenceManyRegister
from server.models.http.requests.schedule_request_models import (
    ScheduleRegister,
    ScheduleUpdate,
)
from server.repositories.occurrence_repository import OccurrenceRepository


class ScheduleRepository:
    @staticmethod
    def get_all(*, session: Session) -> list[Schedule]:
        statement = select(Schedule)
        schedules = session.exec(statement).all()
        return list(schedules)

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> Schedule:
        statement = select(Schedule).where(col(Schedule.id) == id)
        schedule = session.exec(statement).one()
        return schedule

    @staticmethod
    def get_all_on_class(*, class_: Class, session: Session) -> list[Schedule]:
        statement = select(Schedule).where(Schedule.class_id == class_.id)
        schedules = list(session.exec(statement).all())
        return schedules

    @staticmethod
    def get_by_id_on_class(*, class_: Class, id: int, session: Session) -> Schedule:
        statement = (
            select(Schedule)
            .where(Schedule.class_id == class_.id)
            .where(Schedule.id == id)
        )
        schedule = session.exec(statement).one()
        return schedule

    @staticmethod
    def get_by_id_on_building(
        *, schedule_id: int, building: Building, session: Session
    ) -> Schedule:
        statement = select(Schedule).where(Schedule.id == schedule_id)

        try:
            schedule = session.exec(statement).one()
        except NoResultFound:
            raise ScheduleNotFound()

        buildings = schedule.class_.subject.buildings
        if building.id not in [building.id for building in buildings]:
            raise ScheduleNotFound()

        return schedule

    @staticmethod
    def create_with_class(
        *, class_input: Class, input: ScheduleRegister, session: Session
    ) -> Schedule:
        new_schedule = Schedule(
            start_date=input.start_date,
            end_date=input.end_date,
            recurrence=input.recurrence,
            skip_exceptions=input.skip_exceptions,
            all_day=input.all_day,
            allocated=input.allocated if input.allocated else False,
            week_day=input.week_day,
            start_time=input.start_time,
            end_time=input.end_time,
            class_id=class_input.id,
            class_=class_input,
            reservation_id=None,
            classroom_id=None,
        )
        session.add(new_schedule)
        session.commit()
        session.refresh(new_schedule)

        if input.dates and new_schedule.id:
            occurences_input = OccurenceManyRegister(
                classroom_id=None,
                schedule_id=new_schedule.id,
                start_time=input.start_time,
                end_time=input.end_time,
                dates=input.dates,
            )
            occurences = OccurrenceRepository.create_many_with_schedule(
                schedule=new_schedule, input=occurences_input, session=session
            )
            new_schedule.occurrences = occurences
            session.add(new_schedule)
            session.commit()
            session.refresh(new_schedule)

        return new_schedule

    @staticmethod
    def create_many_with_class(
        *, university_class: Class, input: list[ScheduleRegister], session: Session
    ) -> list[Schedule]:
        return [
            ScheduleRepository.create_with_class(
                class_input=university_class, input=schedule_input, session=session
            )
            for schedule_input in input
        ]

    @staticmethod
    def update(*, input: ScheduleUpdate, session: Session) -> None:
        pass

    @staticmethod
    def delete(*, id: int, session: Session) -> None:
        pass


class ScheduleInvalidData(HTTPException):
    def __init__(self, schedule_info: str, data_info: str) -> None:
        super().__init__(
            status.HTTP_400_BAD_REQUEST,
            f"Schedule with {schedule_info} has invalid {data_info} value",
        )


class ScheduleNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=404, detail="Schedule not found")
