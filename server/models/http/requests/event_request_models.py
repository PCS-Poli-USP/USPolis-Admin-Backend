from pydantic import BaseModel
from server.models.http.requests.reservation_request_models import (
    ReservationRegister,
    ReservationUpdate,
)
from server.utils.enums.event_type_enum import EventType
from server.utils.enums.reservation_type import ReservationType


class EventBase(BaseModel):
    type: ReservationType = ReservationType.EVENT
    event_type: EventType
    link: str | None = None


class EventRegister(EventBase, ReservationRegister):
    pass


class EventUpdate(EventBase, ReservationUpdate):
    pass
