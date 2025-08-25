from server.models.http.requests.reservation_request_models import (
    ReservationRegister,
)
from server.utils.enums.event_type_enum import EventType
from server.utils.enums.reservation_type import ReservationType


class EventBase(ReservationRegister):
    type: ReservationType = ReservationType.EVENT
    event_type: EventType
    link: str | None = None


class EventRegister(EventBase):
    pass


class EventUpdate(EventBase):
    pass
