from fastapi import status
from fastapi.testclient import TestClient

from server.models.database.classroom_db_model import Classroom

URL_PREFIX = "/classrooms"


class TestGetAllClassrooms:
    def test_returns_all_classrooms(
        self, public_client: TestClient, classroom: Classroom
    ) -> None:
        response = public_client.get(URL_PREFIX)

        assert response.status_code == status.HTTP_200_OK
        matches = [c for c in response.json() if c["id"] == classroom.id]
        assert len(matches) == 1
        assert matches[0]["name"] == classroom.name


class TestGetAllClassroomsPaginated:
    def test_returns_a_paginated_page(
        self, public_client: TestClient, classroom: Classroom
    ) -> None:
        response = public_client.get(
            f"{URL_PREFIX}/paginated/", params={"page": 1, "page_size": 10}
        )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["page"] == 1
        assert body["page_size"] == 10
        assert classroom.id in [c["id"] for c in body["data"]]


class TestGetAllClassroomsFull:
    def test_returns_classrooms_with_schedules(
        self, public_client: TestClient, classroom: Classroom
    ) -> None:
        response = public_client.get(f"{URL_PREFIX}/full/")

        assert response.status_code == status.HTTP_200_OK
        matches = [c for c in response.json() if c["id"] == classroom.id]
        assert len(matches) == 1
        assert "schedules" in matches[0]
