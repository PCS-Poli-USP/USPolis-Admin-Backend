from datetime import datetime
from pydantic import BaseModel

from server.models.database.class_db_model import Class
from server.models.database.schedule_db_model import Schedule
from server.models.database.subject_db_model import Subject
from server.models.http.exceptions.responses_exceptions import UnfetchDataError
from server.utils.enums.class_type import ClassType


class ClassResponse(BaseModel):
    id: int

    semester: int
    start_date: datetime
    end_date: datetime
    code: str
    class_type: ClassType
    professors: list[str]
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
    updated_at: datetime

    @classmethod
    def from_class(cls, university_class: Class) -> "ClassResponse":
        if university_class.id is None:
            raise UnfetchDataError("Class", "ID")
        input_data = university_class.model_dump()
        class_response_fields = ClassResponse.model_fields.keys()  # type: ignore
        class_response_data = {key: input_data[key] for key in class_response_fields if key in input_data}
        return cls(**class_response_data)

    @classmethod
    def from_class_list(cls, classes: list[Class]) -> list["ClassResponse"]:
        return [cls.from_class(u_class) for u_class in classes]
