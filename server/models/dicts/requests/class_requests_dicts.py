from datetime import datetime
from server.models.dicts.requests.base_requests_dicts import BaseRequestDict
from server.models.http.requests.schedule_request_models import (
    ScheduleRegister,
    ScheduleUpdate,
)
from server.utils.enums.audiovisual_type_enum import AudiovisualType
from server.utils.enums.class_type import ClassType


class ClassRequestBaseDict(BaseRequestDict):
    """Base for any Class request of register or update"""

    calendar_ids: list[int]
    start_date: datetime
    end_date: datetime
    code: str
    type: ClassType
    professors: list[str]
    vacancies: int

    air_conditionating: bool
    accessibility: bool
    audiovisual: AudiovisualType
    ignore_to_allocate: bool


class ClassRegisterDict(ClassRequestBaseDict, total=False):
    subject_id: int
    schedules_data: list[ScheduleRegister]


class ClassUpdateDict(ClassRequestBaseDict, total=False):
    subject_id: int
    schedules_data: list[ScheduleUpdate]
