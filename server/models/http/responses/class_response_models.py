from datetime import date, datetime

from pydantic import BaseModel

from server.models.database.class_db_model import Class
from server.models.http.responses.schedule_response_models import (
    ScheduleResponse,
    ScheduleFullResponse,
)
from server.utils.enums.audiovisual_type_enum import AudiovisualType
from server.utils.enums.class_type import ClassType
from server.utils.must_be_int import must_be_int


class ClassResponseBase(BaseModel):
    id: int
    start_date: date
    end_date: date
    code: str
    professors: list[str]
    type: ClassType
    vacancies: int

    air_conditionating: bool
    accessibility: bool
    audiovisual: AudiovisualType

    ignore_to_allocate: bool
    full_allocated: bool
    updated_at: datetime

    subject_id: int
    subject_building_ids: list[int]
    subject_name: str
    subject_code: str
    calendar_ids: list[int]
    calendar_names: list[str]

    @classmethod
    def from_class(cls, _class: Class) -> "ClassResponseBase":
        return cls(
            id=must_be_int(_class.id),
            start_date=_class.start_date,
            end_date=_class.end_date,
            code=_class.code,
            professors=_class.professors,
            type=_class.type,
            vacancies=_class.vacancies,
            air_conditionating=_class.air_conditionating,
            accessibility=_class.accessibility,
            audiovisual=_class.audiovisual,
            ignore_to_allocate=_class.ignore_to_allocate,
            full_allocated=_class.full_allocated,
            updated_at=_class.updated_at,
            subject_id=must_be_int(_class.subject.id),
            subject_building_ids=[
                building.id for building in _class.subject.buildings if (building.id)
            ],
            subject_code=_class.subject.code,
            subject_name=_class.subject.name,
            calendar_ids=[
                calendar.id for calendar in _class.calendars if (calendar.id)
            ],
            calendar_names=[calendar.name for calendar in _class.calendars],
        )


class ClassResponse(ClassResponseBase):
    """Class basic response"""

    schedules: list[ScheduleResponse]

    @classmethod
    def from_class(cls, _class: Class) -> "ClassResponse":
        base = ClassResponseBase.from_class(_class)
        return cls(
            **base.model_dump(),
            schedules=ScheduleResponse.from_schedule_list(_class.schedules),
        )

    @classmethod
    def from_class_list(cls, classes: list[Class]) -> list["ClassResponse"]:
        return [cls.from_class(u_class) for u_class in classes]


class ClassFullResponse(ClassResponseBase):
    """Class with schedules and occurrences"""

    schedules: list[ScheduleFullResponse]

    @classmethod
    def from_class(cls, _class: Class) -> "ClassFullResponse":
        base = ClassResponseBase.from_class(_class)
        return cls(
            **base.model_dump(),
            schedules=ScheduleFullResponse.from_schedule_list(_class.schedules),
        )

    @classmethod
    def from_class_list(cls, classes: list[Class]) -> list["ClassFullResponse"]:
        return [cls.from_class(u_class) for u_class in classes]
