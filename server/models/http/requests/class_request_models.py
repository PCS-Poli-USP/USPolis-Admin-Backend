from datetime import datetime
from pydantic import BaseModel

from server.models.http.requests.schedule_request_models import (
    ScheduleRegister,
    ScheduleUpdate,
)
from server.utils.enums.class_type import ClassType


class ClassRequestBase(BaseModel):
    """Base for any Class request of register or update"""
    calendar_ids: list[int]
    start_date: datetime
    end_date: datetime
    code: str
    type: ClassType
    professors: list[str]
    vacancies: int
    subscribers: int
    pendings: int

    air_conditionating: bool
    accessibility: bool
    projector: bool

    ignore_to_allocate: bool


class ClassRegister(ClassRequestBase):
    """Class register input body"""

    subject_id: int
    schedules_data: list[ScheduleRegister]


class ClassUpdate(ClassRequestBase):
    """Class update input body"""

    subject_id: int | None = None
    schedules_data: list[ScheduleUpdate] | None = None
