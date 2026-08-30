from server.models.http.responses.event_response_models import EventResponse
from server.utils.enums.event_type_enum import EventType
from server.utils.enums.reservation_type import ReservationType
from tests.utils.academic_test_utils import (
    make_building,
    make_classroom,
    make_event,
    make_reservation,
)
from tests.utils.time_test_utils import make_schedule


class TestEventResponse:
    def test_from_event_includes_reservation(self) -> None:
        classroom = make_classroom(building=make_building())
        schedule = make_schedule(classroom=classroom)
        schedule.occurrences = []
        schedule.logs = []
        reservation = make_reservation(schedule=schedule, type_=ReservationType.EVENT)
        event = make_event(reservation=reservation, type_=EventType.WORKSHOP)

        data = EventResponse.from_event(event)

        assert data.id == event.id
        assert data.type == EventType.WORKSHOP
        assert data.reservation.id == reservation.id

    def test_from_events(self) -> None:
        classroom = make_classroom(building=make_building())
        schedule1 = make_schedule(classroom=classroom)
        schedule1.occurrences = []
        schedule1.logs = []
        reservation1 = make_reservation(schedule=schedule1, type_=ReservationType.EVENT)
        event1 = make_event(reservation=reservation1)

        schedule2 = make_schedule(classroom=classroom)
        schedule2.occurrences = []
        schedule2.logs = []
        reservation2 = make_reservation(schedule=schedule2, type_=ReservationType.EVENT)
        event2 = make_event(reservation=reservation2)

        data = EventResponse.from_events([event1, event2])

        assert [d.id for d in data] == [event1.id, event2.id]
