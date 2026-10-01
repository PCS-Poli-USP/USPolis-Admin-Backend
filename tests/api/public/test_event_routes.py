from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.classroom_db_model import Classroom
from server.models.database.event_db_model import Event

URL_PREFIX = "/reservations/events"


class TestGetAllEvents:
    def test_returns_events_active_today_by_default(
        self,
        public_client: TestClient,
        event: Event,
        classroom: Classroom,
        session: Session,
    ) -> None:
        # EventModelFactory/ReservationModelFactory never actually wire the
        # classroom they're given onto the created schedule, so the fixture
        # event has no classroom/building - required for get_building() to
        # resolve when building the response.
        event.reservation.schedule.classroom = classroom
        session.add(event.reservation.schedule)
        session.commit()

        response = public_client.get(URL_PREFIX)

        assert response.status_code == status.HTTP_200_OK
        matches = [e for e in response.json() if e["id"] == event.id]
        assert len(matches) == 1
        assert matches[0]["type"] == event.type.value
        assert matches[0]["reservation"]["id"] == event.reservation_id

    def test_excludes_events_outside_the_start_end_interval(
        self, public_client: TestClient, event: Event
    ) -> None:
        response = public_client.get(
            URL_PREFIX, params={"start": "1999-01-01", "end": "1999-12-31"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert event.id not in [e["id"] for e in response.json()]
