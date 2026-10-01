from server.models.dicts.base.class_base_dict import ClassBaseDict
from server.models.dicts.requests.base_requests_dicts import BaseRequestDict
from server.models.http.requests.schedule_request_models import (
    ScheduleRegister,
    ScheduleUpdate,
)


class ClassRequestBaseDict(ClassBaseDict, BaseRequestDict, total=False):
    """Base for any Class request of register or update"""

    calendar_ids: list[int]


class ClassRegisterDict(ClassRequestBaseDict, total=False):
    subject_id: int
    schedules_data: list[ScheduleRegister]


class ClassUpdateDict(ClassRequestBaseDict, total=False):
    subject_id: int
    schedules_data: list[ScheduleUpdate]
