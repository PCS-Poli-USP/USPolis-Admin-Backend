from collections.abc import Generator
from datetime import date, datetime, timedelta

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


def first_month(class_: Class) -> dict[str, str]:
    """The class's first 31 days: /allocations/events caps the range there
    (the frontend asks for a day or a week)."""
    start = class_.start_date
    return {
        "start": start.isoformat(),
        "end": (start + timedelta(days=30)).isoformat(),
    }


class TestGetAllAllocationResources:
    def test_returns_building_and_its_non_restricted_classrooms(
        self,
        public_client: TestClient,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        classroom.restricted = False
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
            params=first_month(class_),
        )

        assert response.status_code == status.HTTP_200_OK
        subject_events = [e for e in response.json() if e["type"] == "subject"]
        assert any(class_.subject.code in e["title"] for e in subject_events)

    def test_returns_allocated_occurrences_with_the_classroom(
        self,
        public_client: TestClient,
        class_: Class,
        allocated_classroom: Classroom,
        session: Session,
    ) -> None:
        # get_all_on_interval_for_allocation only includes an allocated
        # occurrence when its classroom isn't restricted.
        allocated_classroom.restricted = False
        session.add(allocated_classroom)
        session.commit()

        response = public_client.get(
            f"{URL_PREFIX}/events",
            params=first_month(class_),
        )

        assert response.status_code == status.HTTP_200_OK
        classrooms = [e["classroom"] for e in response.json()]
        assert allocated_classroom.name in classrooms


class TestAllocationEventsInterval:
    @pytest.mark.parametrize(
        ("start", "end", "expected"),
        [
            ("2026-03-01", "2026-03-31", status.HTTP_200_OK),
            ("2026-03-01", "2026-04-01", status.HTTP_400_BAD_REQUEST),
            ("2026-03-02", "2026-03-01", status.HTTP_400_BAD_REQUEST),
        ],
        ids=["31-days", "32-days", "end-before-start"],
    )
    def test_range_is_capped_at_31_days(
        self, public_client: TestClient, start: str, end: str, expected: int
    ) -> None:
        response = public_client.get(
            f"{URL_PREFIX}/events", params={"start": start, "end": end}
        )

        assert response.status_code == expected

    def test_without_dates_it_uses_todays_date_at_request_time(
        self, public_client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Regression: `date.today()` as a parameter default froze "today" at
        # import time.
        seen: list[tuple[object, object]] = []
        monkeypatch.setattr(
            "server.routes.public.allocation_routes.OccurrenceRepository."
            "get_all_on_interval_for_allocation",
            lambda start, end, session: seen.append((start, end)) or [],
        )
        frozen_today = datetime(2031, 5, 20, 10, 0)
        monkeypatch.setattr(
            "server.routes.public.allocation_routes.BrazilDatetime.now_utc",
            lambda: frozen_today,
        )

        response = public_client.get(f"{URL_PREFIX}/events")

        assert response.status_code == status.HTTP_200_OK
        assert seen == [(date(2031, 5, 20), date(2031, 5, 20))]
