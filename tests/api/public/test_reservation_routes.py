from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.meeting_db_model import Meeting

URL_PREFIX = "/reservations"


class TestGetAllReservations:
    def test_returns_reservations_active_today_by_default(
        self,
        public_client: TestClient,
        meeting: Meeting,
        classroom: Classroom,
        session: Session,
    ) -> None:
        meeting.reservation.schedule.classroom = classroom
        session.add(meeting.reservation.schedule)
        session.commit()

        response = public_client.get(URL_PREFIX)

        assert response.status_code == status.HTTP_200_OK
        assert meeting.reservation_id in [r["id"] for r in response.json()]

    def test_excludes_reservations_outside_the_start_end_interval(
        self, public_client: TestClient, meeting: Meeting
    ) -> None:
        response = public_client.get(
            URL_PREFIX, params={"start": "1999-01-01", "end": "1999-12-31"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert meeting.reservation_id not in [r["id"] for r in response.json()]


class TestGetAllReservationsFull:
    def test_returns_reservations_with_a_full_schedule(
        self,
        public_client: TestClient,
        meeting: Meeting,
        classroom: Classroom,
        session: Session,
    ) -> None:
        meeting.reservation.schedule.classroom = classroom
        session.add(meeting.reservation.schedule)
        session.commit()

        response = public_client.get(f"{URL_PREFIX}/full/")

        assert response.status_code == status.HTTP_200_OK
        matches = [r for r in response.json() if r["id"] == meeting.reservation_id]
        assert len(matches) == 1
        assert "occurrences" in matches[0]["schedule"]


class TestGetAllReservationsByBuildingName:
    def test_returns_reservations_of_the_given_building(
        self,
        public_client: TestClient,
        meeting: Meeting,
        classroom: Classroom,
        building: Building,
        session: Session,
    ) -> None:
        meeting.reservation.schedule.classroom = classroom
        session.add(meeting.reservation.schedule)
        session.commit()

        response = public_client.get(f"{URL_PREFIX}/building/{building.name}")

        assert response.status_code == status.HTTP_200_OK
        assert meeting.reservation_id in [r["id"] for r in response.json()]

    def test_returns_404_for_an_unknown_building(
        self, public_client: TestClient
    ) -> None:
        response = public_client.get(f"{URL_PREFIX}/building/does-not-exist")

        assert response.status_code == status.HTTP_404_NOT_FOUND
