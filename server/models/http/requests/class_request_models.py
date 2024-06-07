from datetime import datetime
from pydantic import BaseModel

from server.models.http.requests.schedule_request_models import ScheduleManyRegister
from server.utils.day_time import DayTime
from server.utils.enums.class_type import ClassType
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay


class ClassBase(BaseModel):
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
    schedules_data: ScheduleManyRegister


class ClassUpdate(ClassBase):
    subject_id: int | None
