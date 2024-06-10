from sqlmodel import Session

from server.models.database.class_db_model import Class
from server.models.database.schedule_db_model import Schedule
from server.models.http.requests.schedule_request_models import (
    ScheduleManyRegister,
    ScheduleRegister,
)


class ScheduleRepository:
    @staticmethod
    def create_with_class(
        *, university_class: Class, input: ScheduleRegister, session: Session
    ) -> Schedule:
        new_schedule = Schedule(**input.model_dump(), university_class=university_class)
        session.add(new_schedule)
        session.commit()
        session.refresh(new_schedule)
        return new_schedule

    @staticmethod
    def create_many_with_class(
        *, university_class: Class, input: ScheduleManyRegister, session: Session
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
                calendar_id=input.calendar_id,
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
                university_class=university_class, input=schedule_input, session=session
            )
            for schedule_input in inputs
        ]
