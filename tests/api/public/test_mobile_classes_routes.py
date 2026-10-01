from collections.abc import Generator
from datetime import date

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.cache import clear_cache
from server.models.database.class_db_model import Class
from server.models.database.subject_db_model import Subject
from tests.factories.model.class_model_factory import ClassModelFactory
from tests.factories.model.schedule_model_factory import ScheduleModelFactory

URL_PREFIX = "/mobile/classes"


@pytest.fixture(autouse=True)
def _clear_response_cache() -> Generator[None, None, None]:
    # get_all_classes is wrapped in @simple_cache with a key based only on
    # the function name (not on the interval query params), so results from
    # one test would otherwise leak into the next via server/cache.py's
    # module-level, process-wide store.
    clear_cache()
    yield
    clear_cache()


def make_class_with_schedule(
    *,
    subject: Subject,
    session: Session,
    class_start: date,
    class_end: date,
    schedule_start: date,
    schedule_end: date,
) -> Class:
    class_ = ClassModelFactory(subject=subject, session=session).create_and_refresh(
        schedules=[], start_date=class_start, end_date=class_end
    )
    ScheduleModelFactory(class_=class_, session=session).create_and_refresh(
        start_date=schedule_start, end_date=schedule_end
    )
    session.refresh(class_)
    return class_


class TestGetAllClasses:
    def test_returns_a_class_active_today_by_default(
        self, public_client: TestClient, subject: Subject, session: Session
    ) -> None:
        class_ = make_class_with_schedule(
            subject=subject,
            session=session,
            class_start=date(2025, 1, 1),
            class_end=date(2025, 12, 31),
            schedule_start=date(2025, 1, 1),
            schedule_end=date(2025, 12, 31),
        )

        response = public_client.get(URL_PREFIX, params={"today": "2025-06-15"})

        assert response.status_code == status.HTTP_200_OK
        matches = [c for c in response.json() if c["id"] == class_.id]
        assert len(matches) == 1
        assert matches[0]["code"] == class_.code
        assert matches[0]["subject_code"] == subject.code
        assert len(matches[0]["schedules"]) == 1

    def test_excludes_classes_that_already_ended_as_of_today(
        self, public_client: TestClient, subject: Subject, session: Session
    ) -> None:
        class_ = make_class_with_schedule(
            subject=subject,
            session=session,
            class_start=date(2024, 1, 1),
            class_end=date(2024, 6, 30),
            schedule_start=date(2024, 1, 1),
            schedule_end=date(2024, 6, 30),
        )

        response = public_client.get(URL_PREFIX, params={"today": "2025-06-15"})

        assert class_.id not in [c["id"] for c in response.json()]

    def test_excludes_classes_outside_the_start_end_interval(
        self, public_client: TestClient, subject: Subject, session: Session
    ) -> None:
        class_ = make_class_with_schedule(
            subject=subject,
            session=session,
            class_start=date(2025, 1, 1),
            class_end=date(2025, 6, 30),
            schedule_start=date(2025, 1, 1),
            schedule_end=date(2025, 6, 30),
        )

        response = public_client.get(
            URL_PREFIX, params={"start": "2025-07-01", "end": "2025-12-31"}
        )

        assert class_.id not in [c["id"] for c in response.json()]

    def test_includes_classes_within_the_start_end_interval(
        self, public_client: TestClient, subject: Subject, session: Session
    ) -> None:
        class_ = make_class_with_schedule(
            subject=subject,
            session=session,
            class_start=date(2025, 1, 1),
            class_end=date(2025, 12, 31),
            schedule_start=date(2025, 1, 1),
            schedule_end=date(2025, 6, 30),
        )

        response = public_client.get(
            URL_PREFIX, params={"start": "2025-01-01", "end": "2025-12-31"}
        )

        assert class_.id in [c["id"] for c in response.json()]

    def test_includes_a_schedule_starting_after_interval_start(
        self, public_client: TestClient, subject: Subject, session: Session
    ) -> None:
        class_ = ClassModelFactory(subject=subject, session=session).create_and_refresh(
            schedules=[], start_date=date(2025, 1, 1), end_date=date(2025, 12, 31)
        )
        ScheduleModelFactory(class_=class_, session=session).create_and_refresh(
            start_date=date(2025, 1, 1), end_date=date(2025, 6, 30)
        )
        ScheduleModelFactory(class_=class_, session=session).create_and_refresh(
            start_date=date(2025, 3, 1), end_date=date(2025, 6, 30)
        )
        session.refresh(class_)

        response = public_client.get(
            URL_PREFIX, params={"start": "2025-01-01", "end": "2025-12-31"}
        )

        matches = [c for c in response.json() if c["id"] == class_.id]
        assert len(matches) == 1
        assert len(matches[0]["schedules"]) == 2
