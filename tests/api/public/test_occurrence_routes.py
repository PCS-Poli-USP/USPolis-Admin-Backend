from fastapi import status
from fastapi.testclient import TestClient

from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom

URL_PREFIX = "/occurrences"


class TestGetAllOccurrences:
    def test_returns_occurrences_for_an_allocated_schedule(
        self, client: TestClient, class_: Class, allocated_classroom: Classroom
    ) -> None:
        response = client.get(URL_PREFIX)

        assert response.status_code == status.HTTP_200_OK
        classrooms = [o["classroom"] for o in response.json()]
        assert allocated_classroom.name in classrooms

    def test_returns_empty_when_nothing_is_allocated(
        self, client: TestClient, class_: Class
    ) -> None:
        response = client.get(URL_PREFIX)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_requires_authentication(self, public_client: TestClient) -> None:
        response = public_client.get(URL_PREFIX)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetScheduleResponse:
    def test_returns_the_schedule(
        self, client: TestClient, class_: Class
    ) -> None:
        schedule = class_.schedules[0]

        response = client.get(f"{URL_PREFIX}/schedule/{schedule.id}")

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["id"] == schedule.id
        assert body["class_id"] == class_.id


class TestGetOccurrencesByScheduleFull:
    def test_returns_the_schedule_with_occurrences_and_logs(
        self, client: TestClient, class_: Class, allocated_classroom: Classroom
    ) -> None:
        schedule = class_.schedules[0]

        response = client.get(f"{URL_PREFIX}/schedule/full/{schedule.id}")

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["id"] == schedule.id
        assert isinstance(body["occurrences"], list)
        assert len(body["occurrences"]) > 0
        assert isinstance(body["logs"], list)
