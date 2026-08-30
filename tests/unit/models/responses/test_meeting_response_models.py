from server.models.http.responses.meeting_response_models import MeetingResponse
from server.utils.enums.reservation_type import ReservationType
from tests.utils.academic_test_utils import (
    make_building,
    make_classroom,
    make_meeting,
    make_reservation,
)
from tests.utils.time_test_utils import make_schedule


class TestMeetingResponse:
    def test_from_meeting_includes_reservation(self) -> None:
        classroom = make_classroom(building=make_building())
        schedule = make_schedule(classroom=classroom)
        schedule.occurrences = []
        schedule.logs = []
        reservation = make_reservation(schedule=schedule, type_=ReservationType.MEETING)
        meeting = make_meeting(reservation=reservation, link="https://meet.com")

        data = MeetingResponse.from_meeting(meeting)

        assert data.id == meeting.id
        assert data.link == "https://meet.com"
        assert data.reservation.id == reservation.id

    def test_from_meetings(self) -> None:
        classroom = make_classroom(building=make_building())
        schedule1 = make_schedule(classroom=classroom)
        schedule1.occurrences = []
        schedule1.logs = []
        reservation1 = make_reservation(schedule=schedule1, type_=ReservationType.MEETING)
        meeting1 = make_meeting(reservation=reservation1)

        schedule2 = make_schedule(classroom=classroom)
        schedule2.occurrences = []
        schedule2.logs = []
        reservation2 = make_reservation(schedule=schedule2, type_=ReservationType.MEETING)
        meeting2 = make_meeting(reservation=reservation2)

        data = MeetingResponse.from_meetings([meeting1, meeting2])

        assert [d.id for d in data] == [meeting1.id, meeting2.id]
