from server.models.http.responses.reservation_response_models import (
    ReservationFullResponse,
    ReservationResponse,
)
from server.utils.enums.reservation_type import ReservationType
from tests.utils.academic_test_utils import (
    make_building,
    make_classroom,
    make_event,
    make_meeting,
    make_reservation,
)
from tests.utils.time_test_utils import make_schedule


class TestReservationResponse:
    def test_from_reservation_without_any_specialization(self) -> None:
        classroom = make_classroom(building=make_building())
        schedule = make_schedule(classroom=classroom)
        schedule.occurrences = []
        schedule.logs = []
        reservation = make_reservation(schedule=schedule)
        reservation.exam = None
        reservation.meeting = None
        reservation.event = None

        data = ReservationResponse.from_reservation(reservation)

        assert data.id == reservation.id
        assert data.exam is None
        assert data.meeting is None
        assert data.event is None

    def test_from_reservation_with_a_meeting(self) -> None:
        classroom = make_classroom(building=make_building())
        schedule = make_schedule(classroom=classroom)
        schedule.occurrences = []
        schedule.logs = []
        reservation = make_reservation(schedule=schedule, type_=ReservationType.MEETING)
        reservation.exam = None
        reservation.event = None
        meeting = make_meeting(reservation=reservation)

        data = ReservationResponse.from_reservation(reservation)

        assert data.meeting is not None
        assert data.meeting.id == meeting.id

    def test_from_reservation_with_an_event(self) -> None:
        classroom = make_classroom(building=make_building())
        schedule = make_schedule(classroom=classroom)
        schedule.occurrences = []
        schedule.logs = []
        reservation = make_reservation(schedule=schedule, type_=ReservationType.EVENT)
        reservation.exam = None
        reservation.meeting = None
        event = make_event(reservation=reservation)

        data = ReservationResponse.from_reservation(reservation)

        assert data.event is not None
        assert data.event.id == event.id

    def test_from_reservation_list(self) -> None:
        classroom = make_classroom(building=make_building())
        schedule1 = make_schedule(classroom=classroom)
        schedule1.occurrences = []
        schedule1.logs = []
        reservation1 = make_reservation(schedule=schedule1)
        reservation1.exam = None
        reservation1.meeting = None
        reservation1.event = None

        schedule2 = make_schedule(classroom=classroom)
        schedule2.occurrences = []
        schedule2.logs = []
        reservation2 = make_reservation(schedule=schedule2)
        reservation2.exam = None
        reservation2.meeting = None
        reservation2.event = None

        data = ReservationResponse.from_reservation_list([reservation1, reservation2])

        assert [d.id for d in data] == [reservation1.id, reservation2.id]


class TestReservationFullResponse:
    def test_from_reservation_includes_full_schedule(self) -> None:
        classroom = make_classroom(building=make_building())
        schedule = make_schedule(classroom=classroom)
        schedule.occurrences = []
        schedule.logs = []
        reservation = make_reservation(schedule=schedule)

        data = ReservationFullResponse.from_reservation(reservation)

        assert data.schedule.id == schedule.id
        assert data.schedule.occurrences == []
        assert data.schedule.logs == []

    def test_from_reservation_list(self) -> None:
        classroom = make_classroom(building=make_building())
        schedule1 = make_schedule(classroom=classroom)
        schedule1.occurrences = []
        schedule1.logs = []
        reservation1 = make_reservation(schedule=schedule1)

        schedule2 = make_schedule(classroom=classroom)
        schedule2.occurrences = []
        schedule2.logs = []
        reservation2 = make_reservation(schedule=schedule2)

        data = ReservationFullResponse.from_reservation_list([reservation1, reservation2])

        assert [d.id for d in data] == [reservation1.id, reservation2.id]
