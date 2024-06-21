from datetime import date, datetime

from pydantic import BaseModel

from server.models.database.class_db_model import Class
from server.models.http.exceptions.responses_exceptions import UnfetchDataError
from server.models.http.responses.schedule_response_models import ScheduleResponse
from server.utils.enums.class_type import ClassType


class ClassResponseBase(BaseModel):
    id: int
    start_date: date
    end_date: date
    code: str
    professors: list[str]
    type: ClassType
    vacancies: int
    subscribers: int
    pendings: int

    air_conditionating: bool
    accessibility: bool
    projector: bool

    ignore_to_allocate: bool
    full_allocated: bool
    updated_at: datetime


class ClassResponse(ClassResponseBase):
    subject_id: int
    subject_name: str
    subject_code: str
    schedules: list[ScheduleResponse]
    calendar_ids: list[int] | None = None
    calendar_names: list[str] | None = None

    @classmethod
    def from_class(cls, _class: Class) -> "ClassResponse":
        if _class.id is None:
            raise UnfetchDataError("Class", "ID")
        if _class.subject.id is None:
            raise UnfetchDataError("Subject", "ID")
        return cls(
            id=_class.id,
            start_date=_class.start_date,
            end_date=_class.end_date,
            code=_class.code,
            professors=_class.professors,
            type=_class.type,
            vacancies=_class.vacancies,
            subscribers=_class.subscribers,
            pendings=_class.pendings,
            air_conditionating=_class.air_conditionating,
            accessibility=_class.accessibility,
            projector=_class.projector,
            ignore_to_allocate=_class.ignore_to_allocate,
            full_allocated=_class.full_allocated,
            updated_at=_class.updated_at,
            subject_id=_class.subject.id,
            subject_code=_class.subject.code,
            subject_name=_class.subject.name,
            schedules=ScheduleResponse.from_schedule_list(_class.schedules),
            calendar_ids=[
                calendar.id for calendar in _class.calendars if (calendar.id)
            ] if _class.calendars else None,
            calendar_names=[
                calendar.name for calendar in _class.calendars] if _class.calendars else None,
        )

    @classmethod
    def from_class_list(cls, classes: list[Class]) -> list["ClassResponse"]:
        return [cls.from_class(u_class) for u_class in classes]
