from datetime import datetime
from pydantic import BaseModel

from server.utils.enums.class_type import ClassType
from server.utils.enums.recurrence import Recurrence


class ClassBase(BaseModel):
    week_days: list[str]
    start_times: list[str]
    end_times: list[str]
    recurrence: Recurrence

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


class ClassRegister(ClassBase):
    subject_id: int


class ClassUpdate(ClassBase):
    subject_id: int | None
