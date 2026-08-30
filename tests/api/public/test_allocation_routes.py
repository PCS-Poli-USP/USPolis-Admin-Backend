from collections.abc import Generator

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.cache import clear_cache
from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom

URL_PREFIX = "/allocations"


@pytest.fixture(autouse=True)
def _clear_response_cache() -> Generator[None, None, None]:
    # get_all_allocation_events is wrapped in @date_range_cache, which is a
    # module-level, process-wide store like @simple_cache.
    clear_cache()
    yield
    clear_cache()


class TestGetAllAllocationResources:
    def test_returns_building_and_its_non_remote_classrooms(
        self,
        public_client: TestClient,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        classroom.remote = False
        session.add(classroom)
        session.commit()

        response = public_client.get(f"{URL_PREFIX}/resources")

        assert response.status_code == status.HTTP_200_OK
        ids = [r["id"] for r in response.json()]
        assert building.name in ids
        assert f"{building.name}-{classroom.name}" in ids

    def test_always_appends_unallocated_sentinels(
        self, public_client: TestClient, building: Building
    ) -> None:
        response = public_client.get(f"{URL_PREFIX}/resources")

        assert response.status_code == status.HTTP_200_OK
        titles = [r["title"] for r in response.json()]
        assert titles.count("Não alocada") == 2


class TestGetAllAllocationEvents:
    def test_returns_unallocated_class_schedule_as_a_subject_event(
        self, public_client: TestClient, class_: Class
    ) -> None:
        response = public_client.get(
            f"{URL_PREFIX}/events",
            params={
                "start": class_.start_date.isoformat(),
                "end": class_.end_date.isoformat(),
            },
        )

        assert response.status_code == status.HTTP_200_OK
        subject_events = [e for e in response.json() if e["type"] == "subject"]
        assert any(
            class_.subject.code in e["title"] for e in subject_events
        )

    def test_returns_allocated_occurrences_with_the_classroom(
        self,
        public_client: TestClient,
        class_: Class,
        allocated_classroom: Classroom,
        session: Session,
    ) -> None:
        # get_all_on_interval_for_allocation only includes an allocated
        # occurrence when its classroom isn't remote.
        allocated_classroom.remote = False
        session.add(allocated_classroom)
        session.commit()

        response = public_client.get(
            f"{URL_PREFIX}/events",
            params={
                "start": class_.start_date.isoformat(),
                "end": class_.end_date.isoformat(),
            },
        )

        assert response.status_code == status.HTTP_200_OK
        classrooms = [e["classroom"] for e in response.json()]
        assert allocated_classroom.name in classrooms
