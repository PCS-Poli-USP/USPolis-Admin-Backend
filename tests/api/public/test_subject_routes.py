from fastapi import status
from fastapi.testclient import TestClient

from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.subject_db_model import Subject

URL_PREFIX = "/subjects"


class TestGetAllSubjects:
    def test_returns_all_subjects_with_buildings(
        self, public_client: TestClient, subject: Subject, building: Building
    ) -> None:
        response = public_client.get(URL_PREFIX)

        assert response.status_code == status.HTTP_200_OK
        matches = [s for s in response.json() if s["id"] == subject.id]
        assert len(matches) == 1
        assert matches[0]["code"] == subject.code
        assert matches[0]["building_ids"] == [building.id]
        assert matches[0]["buildings"][0]["name"] == building.name


class TestGetAllSubjectsCore:
    def test_returns_subjects_without_building_data(
        self, public_client: TestClient, subject: Subject
    ) -> None:
        response = public_client.get(f"{URL_PREFIX}/core")

        assert response.status_code == status.HTTP_200_OK
        matches = [s for s in response.json() if s["id"] == subject.id]
        assert len(matches) == 1
        assert "buildings" not in matches[0]
        assert "building_ids" not in matches[0]


class TestGetAllSubjectsActive:
    def test_returns_subjects_with_classes_in_the_interval(
        self, public_client: TestClient, subject: Subject, class_: Class
    ) -> None:
        response = public_client.get(
            f"{URL_PREFIX}/actives",
            params={
                "start": class_.start_date.isoformat(),
                "end": class_.end_date.isoformat(),
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert subject.id in [s["id"] for s in response.json()]

    def test_excludes_subjects_without_classes_in_the_interval(
        self, public_client: TestClient, subject: Subject, class_: Class
    ) -> None:
        response = public_client.get(
            f"{URL_PREFIX}/actives",
            params={"start": "1999-01-01", "end": "1999-12-31"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert subject.id not in [s["id"] for s in response.json()]
