from server.models.dicts.base.reservation_base_dict import ReservationBaseDict
from server.models.dicts.requests.base_requests_dicts import BaseRequestDict
from server.models.http.requests.schedule_request_models import (
    ScheduleRegister,
    ScheduleUpdate,
)


class ReservationRegisterDict(ReservationBaseDict, BaseRequestDict, total=False):
    classroom_id: int
    schedule_data: ScheduleRegister


class ReservationUpdateDict(ReservationBaseDict, BaseRequestDict, total=False):
    classroom_id: int
    schedule_data: ScheduleUpdate
