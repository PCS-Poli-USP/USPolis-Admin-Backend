from sqlmodel import Session

from server.models.database.class_db_model import Class
from server.models.database.schedule_db_model import Schedule
from server.models.http.requests.schedule_request_models import (
    ScheduleRegister,
)


class ScheduleRepository:
    @staticmethod
    def create_with_class(
        *, university_class: Class, input: ScheduleRegister, session: Session
    ) -> Schedule:
        new_schedule = Schedule(**input.model_dump(), class_=university_class)
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
                university_class=university_class, input=schedule_input, session=session
            )
            for schedule_input in input
        ]
