from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.classroom_db_model import Classroom
from server.models.database.meeting_db_model import Meeting

URL_PREFIX = "/reservations/meetings"


class TestGetAllMeetings:
    def test_returns_meetings_active_today_by_default(
        self,
        public_client: TestClient,
        meeting: Meeting,
        classroom: Classroom,
        session: Session,
    ) -> None:
        # MeetingModelFactory/ReservationModelFactory never actually wire the
        # classroom they're given onto the created schedule, so the fixture
        # meeting has no classroom/building - required for get_building() to
        # resolve when building the response.
        meeting.reservation.schedule.classroom = classroom
        session.add(meeting.reservation.schedule)
        session.commit()

        response = public_client.get(URL_PREFIX)

        assert response.status_code == status.HTTP_200_OK
        matches = [m for m in response.json() if m["id"] == meeting.id]
        assert len(matches) == 1
        assert matches[0]["reservation"]["id"] == meeting.reservation_id

    def test_excludes_meetings_outside_the_start_end_interval(
        self, public_client: TestClient, meeting: Meeting
    ) -> None:
        response = public_client.get(
            URL_PREFIX, params={"start": "1999-01-01", "end": "1999-12-31"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert meeting.id not in [m["id"] for m in response.json()]
