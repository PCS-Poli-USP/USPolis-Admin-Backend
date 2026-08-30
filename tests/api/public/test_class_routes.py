from datetime import date, timedelta

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.subject_db_model import Subject
from server.utils.brazil_datetime import BrazilDatetime
from tests.factories.model.occurrence_model_factory import OccurrenceModelFactory

URL_PREFIX = "/classes"


class TestGetAllClasses:
    def test_returns_all_active_classes(
        self, public_client: TestClient, class_: Class
    ) -> None:
        response = public_client.get(URL_PREFIX)

        assert response.status_code == status.HTTP_200_OK
        assert class_.id in [c["id"] for c in response.json()]

    def test_excludes_classes_outside_the_start_end_interval(
        self, public_client: TestClient, class_: Class
    ) -> None:
        response = public_client.get(
            URL_PREFIX, params={"start": "1999-01-01", "end": "1999-12-31"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert class_.id not in [c["id"] for c in response.json()]


class TestGetAllClassesFull:
    def test_returns_classes_with_schedules(
        self, public_client: TestClient, class_: Class
    ) -> None:
        response = public_client.get(f"{URL_PREFIX}/full/")

        assert response.status_code == status.HTTP_200_OK
        matches = [c for c in response.json() if c["id"] == class_.id]
        assert len(matches) == 1
        assert "schedules" in matches[0]


class TestGetAllClassesBySubject:
    def test_returns_classes_of_the_given_subject(
        self, public_client: TestClient, class_: Class, subject: Subject
    ) -> None:
        response = public_client.get(f"{URL_PREFIX}/subject/{subject.id}")

        assert response.status_code == status.HTTP_200_OK
        assert class_.id in [c["id"] for c in response.json()]

    def test_returns_empty_for_a_subject_with_no_classes(
        self, public_client: TestClient, class_: Class
    ) -> None:
        response = public_client.get(f"{URL_PREFIX}/subject/999999")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []


class TestGetAllClassesAllocatedByBuildingName:
    def test_returns_classes_allocated_in_the_given_building(
        self,
        public_client: TestClient,
        allocated_classroom: Classroom,
        building: Building,
        class_: Class,
    ) -> None:
        response = public_client.get(f"{URL_PREFIX}/building/{building.name}")

        assert response.status_code == status.HTTP_200_OK
        assert class_.id in [c["id"] for c in response.json()]

    def test_returns_404_for_an_unknown_building(
        self, public_client: TestClient
    ) -> None:
        response = public_client.get(f"{URL_PREFIX}/building/does-not-exist")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetCommingClasses:
    def test_returns_classes_with_an_occurrence_in_the_next_two_days(
        self, public_client: TestClient, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]
        OccurrenceModelFactory(schedule=schedule, session=session).create_and_refresh(
            date=BrazilDatetime.now_utc().date() + timedelta(days=1)
        )

        response = public_client.get(f"{URL_PREFIX}/comming")

        assert response.status_code == status.HTTP_200_OK
        assert class_.id in [c["id"] for c in response.json()]

    def test_excludes_classes_without_an_upcoming_occurrence(
        self, public_client: TestClient, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]
        OccurrenceModelFactory(schedule=schedule, session=session).create_and_refresh(
            date=date(2000, 1, 1)
        )

        response = public_client.get(f"{URL_PREFIX}/comming")

        assert response.status_code == status.HTTP_200_OK
        assert class_.id not in [c["id"] for c in response.json()]
