from server.models.dicts.base.event_base_dict import EventBaseDict
from server.models.dicts.requests.base_requests_dicts import BaseRequestDict
from server.models.dicts.requests.reservation_requests_dicts import (
    ReservationRegisterDict,
    ReservationUpdateDict,
)
from server.utils.enums.event_type_enum import EventType


class EventRegisterDict(
    ReservationRegisterDict, EventBaseDict, BaseRequestDict, total=False
):
    event_type: EventType


class EventUpdateDict(
    ReservationUpdateDict, EventBaseDict, BaseRequestDict, total=False
):
    event_type: EventType
