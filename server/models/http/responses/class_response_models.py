from datetime import date

from pydantic import BaseModel

from server.models.database.class_db_model import Class
from server.models.database.subject_db_model import Subject
from server.models.http.exceptions.responses_exceptions import UnfetchDataError
from server.models.http.responses.schedule_response_models import ScheduleResponse
from server.utils.enums.class_type import ClassType


class ClassResponse(BaseModel):
    id: int
    semester: int
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
    updated_at: date
    subject: Subject
    schedules: list[ScheduleResponse]

    @classmethod
    def from_class(cls, class_in: Class) -> "ClassResponse":
        if class_in.id is None:
            raise UnfetchDataError("Class", "ID")
        return cls(
            id=class_in.id,
            semester=class_in.semester or 0,
            start_date=class_in.start_date,
            end_date=class_in.end_date,
            code=class_in.code,
            professors=class_in.professors,
            type=class_in.type,
            vacancies=class_in.vacancies,
            subscribers=class_in.subscribers,
            pendings=class_in.pendings,
            air_conditionating=class_in.air_conditionating,
            accessibility=class_in.accessibility,
            projector=class_in.projector,
            ignore_to_allocate=class_in.ignore_to_allocate,
            full_allocated=class_in.full_allocated,
            updated_at=class_in.updated_at,
            subject=class_in.subject,
            schedules=ScheduleResponse.from_schedule_list(class_in.schedules),
        )

    @classmethod
    def from_class_list(cls, classes: list[Class]) -> list["ClassResponse"]:
        return [cls.from_class(u_class) for u_class in classes]
