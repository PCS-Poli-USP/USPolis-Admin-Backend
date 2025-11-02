from server.models.dicts.base.meeting_base_dict import MeetingBaseDict
from server.models.dicts.requests.base_requests_dicts import BaseRequestDict
from server.models.dicts.requests.reservation_requests_dicts import (
    ReservationRegisterDict,
    ReservationUpdateDict,
)


class MeetingRegisterDict(
    ReservationRegisterDict, MeetingBaseDict, BaseRequestDict, total=False
):
    pass


class MeetingUpdateDict(
    ReservationUpdateDict, MeetingBaseDict, BaseRequestDict, total=False
):
    pass
