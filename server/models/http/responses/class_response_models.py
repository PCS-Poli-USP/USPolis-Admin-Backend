from datetime import datetime
from pydantic import BaseModel

from server.models.database.class_db_model import Class
from server.models.database.schedule_db_model import Schedule
from server.models.database.subject_db_model import Subject
from server.models.http.exceptions.responses_exceptions import UnfetchDataError
from server.utils.enums.class_type import ClassType


class ClassResponse(BaseModel):
    id: int

    period: list[str]
    start_date: datetime
    end_date: datetime
    class_type: ClassType
    vacancies: int
    subscribers: int
    pendings: int

    air_conditionating: bool
    accessibility: bool
    projector: bool

    ignore_to_allocate: bool
    full_allocated: bool

    subject: Subject
    schedules: list[Schedule]

    @classmethod
    def from_class(cls, university_class: Class) -> "ClassResponse":
        if university_class.id is None:
            raise UnfetchDataError("Class", "ID")
        return cls(**university_class.model_dump())

    @classmethod
    def from_class_list(cls, classes: list[Class]) -> list["ClassResponse"]:
        return [cls.from_class(u_class) for u_class in classes]
