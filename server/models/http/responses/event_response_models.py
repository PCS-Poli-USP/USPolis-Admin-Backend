from typing import Self

from server.models.database.event_db_model import Event
from server.models.http.responses.reservation_response_base import (
    EventResponseBase,
    ReservationCoreResponse,
)


class EventResponse(EventResponseBase):
    reservation: ReservationCoreResponse

    @classmethod
    def from_event(cls, event: Event) -> Self:
        base = super().from_event(event)
        return cls(
            **base.model_dump(),
            reservation=ReservationCoreResponse.from_reservation(event.reservation),
        )

    @classmethod
    def from_events(cls, events: list[Event]) -> list[Self]:
        return [cls.from_event(event) for event in events]
