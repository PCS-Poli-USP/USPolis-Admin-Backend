from datetime import datetime
from pydantic import BaseModel

from server.models.database.class_db_model import Class
from server.models.database.schedule_db_model import Schedule
from server.models.database.subject_db_model import Subject
from server.models.http.exceptions.responses_exceptions import UnfetchDataError
from server.models.http.responses.schedule_response_models import ScheduleResponse
from server.utils.enums.class_type import ClassType


class ClassResponse(BaseModel):
    id: int
    semester: int
    start_date: datetime
    end_date: datetime
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
    subject: Subject
    schedules: list[ScheduleResponse]

    @classmethod
    def from_class(cls, university_class: Class) -> "ClassResponse":
        if university_class.id is None:
            raise UnfetchDataError("Class", "ID")
        return cls(
            id=university_class.id,
            semester=university_class.semester,
            start_date=university_class.start_date,
            end_date=university_class.end_date,
            code=university_class.code,
            professors=university_class.professors,
            type=university_class.type,
            vacancies=university_class.vacancies,
            subscribers=university_class.subscribers,
            pendings=university_class.pendings,
            air_conditionating=university_class.air_conditionating,
            accessibility=university_class.accessibility,
            projector=university_class.projector,
            ignore_to_allocate=university_class.ignore_to_allocate,
            full_allocated=university_class.full_allocated,
            updated_at=university_class.updated_at,
            subject=university_class.subject,
            schedules=ScheduleResponse.from_schedule_list(university_class.schedules),
        )

    @classmethod
    def from_class_list(cls, classes: list[Class]) -> list["ClassResponse"]:
        return [cls.from_class(u_class) for u_class in classes]
