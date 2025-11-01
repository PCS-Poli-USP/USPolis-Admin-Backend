from server.models.database.event_db_model import Event
from server.models.http.requests.event_request_models import EventRegister, EventUpdate
from tests.utils.validators.reservation.reservation_model_validator import (
    ReservationModelAsserts,
)


class EventModelAsserts:
    @staticmethod
    def assert_event_after_create(event: Event, input: EventRegister) -> None:
        reservation = event.reservation
        ReservationModelAsserts.assert_reservation_after_create(reservation, input)

        assert event.type == input.event_type
        assert event.link == input.link

    @staticmethod
    def assert_event_after_update(event: Event, input: EventUpdate) -> None:
        reservation = event.reservation
        ReservationModelAsserts.assert_reservation_after_update(reservation, input)

        assert event.type == input.event_type
        assert event.link == input.link
