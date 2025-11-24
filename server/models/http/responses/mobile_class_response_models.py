from datetime import date
from pydantic import BaseModel

from server.deps.interval_dep import QueryInterval
from server.models.database.class_db_model import Class
from server.models.http.exceptions.responses_exceptions import UnfetchDataError
from server.models.http.responses.mobile_schedule_response_models import (
    MobileScheduleResponse,
)
from server.utils.must_be_int import must_be_int


class MobileClassResponse(BaseModel):
    id: int
    start_date: date
    end_date: date
    code: str
    professors: list[str]
    subject_name: str
    subject_code: str
    subject_id: int
    schedules: list[MobileScheduleResponse]

    @classmethod
    def from_model(
        cls, _class: Class, interval: QueryInterval | None = None
    ) -> "MobileClassResponse":
        if _class.id is None:
            raise UnfetchDataError("Class", "ID")
        if _class.subject.id is None:
            raise UnfetchDataError("Subject", "ID")
        schedules = _class.schedules
        if interval:
            if interval.today:
                schedules = [
                    schedule
                    for schedule in _class.schedules
                    if schedule.start_date >= interval.today
                ]
            if interval.start and interval.end:
                schedules = [
                    schedule
                    for schedule in schedules
                    if interval.start <= schedule.start_date <= interval.end
                ]
        schedules = _class.schedules
        if interval:
            if interval.today:
                schedules = [
                    schedule
                    for schedule in _class.schedules
                    if schedule.end_date >= interval.today
                ]
            if interval.start and interval.end:
                schedules = [
                    schedule
                    for schedule in schedules
                    if interval.start >= schedule.start_date
                    and schedule.end_date <= interval.end
                ]
        return cls(
            id=_class.id,
            start_date=_class.start_date,
            end_date=_class.end_date,
            code=_class.code,
            professors=_class.professors,
            subject_name=_class.subject.name,
            subject_code=_class.subject.code,
            subject_id=must_be_int(_class.subject_id),
            schedules=MobileScheduleResponse.from_schedule_list(schedules),
        )

    @classmethod
    def from_model_list(
        cls, classes: list[Class], interval: QueryInterval | None = None
    ) -> list["MobileClassResponse"]:
        return [cls.from_model(u_class, interval) for u_class in classes]
