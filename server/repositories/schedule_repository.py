from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.schedule_db_model import Schedule
from server.models.http.requests.schedule_request_models import (
    ScheduleManyRegister,
    ScheduleRegister,
)


class ScheduleRepository:
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
        new_schedule = Schedule(**input.model_dump(), class_=class_input)
        session.add(new_schedule)
        session.commit()
        session.refresh(new_schedule)
        return new_schedule

    @staticmethod
    def create_many_with_class(
        *, class_input: Class, input: ScheduleManyRegister, session: Session
    ) -> list[Schedule]:
        days = input.week_days
        starts = input.start_times
        ends = input.end_times

        if len(days) != len(starts) or len(starts) != len(ends):
            raise ValueError("Schedule arrays must be with same size")

        inputs: list[ScheduleRegister] = []
        for i in range(len(days)):
            schedule_input = ScheduleRegister(
                week_day=input.week_days[i],
                start_time=input.start_times[i],
                end_time=input.end_times[i],
                calendar_ids=input.calendar_ids,
                start_date=input.start_date,
                end_date=input.end_date,
                recurrence=input.recurrence,
                skip_exceptions=input.skip_exceptions,
                all_day=input.all_day,
                allocated=input.allocated,
            )
            inputs.append(schedule_input)
        return [
            ScheduleRepository.create_with_class(
                class_input=class_input, input=schedule_input, session=session
            )
            for schedule_input in inputs
        ]


class ScheduleNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=404, detail="Schedule not found")
