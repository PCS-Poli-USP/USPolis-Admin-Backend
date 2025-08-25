from typing import Self
from pydantic import BaseModel

from server.models.database.event_db_model import Event
from server.models.http.responses.reservation_response_models import ReservationResponse
from server.utils.enums.event_type_enum import EventType
from server.utils.must_be_int import must_be_int


class EventResponse(BaseModel):
    id: int
    reservation_id: int
    link: str | None
    type: EventType

    reservation: ReservationResponse

    @classmethod
    def from_event(cls, event: Event) -> Self:
        return cls(
            id=must_be_int(event.id),
            reservation_id=event.reservation_id,
            link=event.link,
            type=event.type,
            reservation=ReservationResponse.from_reservation(event.reservation),
        )
