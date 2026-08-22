"""Route-level evidence for a reported false-positive conflict bug: the
frontend showed a conflict for touching-but-not-overlapping bookings like
[14:00-16:00] vs [16:00-18:00], even after shrinking the second range's start.
These tests drive the actual `with-conflict-count` HTTP routes end-to-end
(the ones the frontend calls), not just the underlying model logic already
covered in tests/unit/models/test_occurrence_model.py, to rule the backend in
or out as the source.
"""

from datetime import date, time

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.occurrence_db_model import Occurrence
from server.utils.enums.recurrence import Recurrence
from server.utils.must_be_int import must_be_int
from tests.factories.model.schedule_model_factory import ScheduleModelFactory

URL_PREFIX = "/classrooms"
TEST_DATE = date(2026, 1, 5)


def _add_occurrence(
    session: Session,
    classroom: Classroom,
    schedule_id: int,
    start_time: time,
    end_time: time,
) -> Occurrence:
    occurrence = Occurrence(
        start_time=start_time,
        end_time=end_time,
        date=TEST_DATE,
        classroom_id=classroom.id,
        schedule_id=schedule_id,
    )
    session.add(occurrence)
    session.commit()
    session.refresh(classroom)
    return occurrence


def _conflicts_for_classroom(response_json: list[dict], classroom_id: int) -> int:
    entry = next(item for item in response_json if item["id"] == classroom_id)
    return int(entry["conflicts"])


def test_post_with_conflict_count_does_not_flag_touching_ranges(
    classroom: Classroom, class_: Class, client: TestClient, session: Session
) -> None:
    """[14:00-16:00] already booked in the classroom; asking about
    [16:00-18:00] on the same date must report 0 conflicts (the exact
    scenario reported as a false positive)."""
    schedule = ScheduleModelFactory(session=session, class_=class_).create_and_refresh(
        allocated=True
    )
    _add_occurrence(
        session, classroom, must_be_int(schedule.id), time(14, 0), time(16, 0)
    )

    response = client.post(
        f"{URL_PREFIX}/with-conflict-count/{classroom.building_id}",
        json={
            "start_time": "16:00:00",
            "end_time": "18:00:00",
            "recurrence": Recurrence.CUSTOM.value,
            "dates": [TEST_DATE.isoformat()],
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert _conflicts_for_classroom(response.json(), must_be_int(classroom.id)) == 0


def test_post_with_conflict_count_flags_genuine_near_boundary_overlap(
    classroom: Classroom, class_: Class, client: TestClient, session: Session
) -> None:
    """[14:00-16:00] already booked; asking about [15:59-17:59] (a genuine
    1-minute overlap — the user's "shrink to 15:59" attempt) must still
    report a conflict, since it really does overlap."""
    schedule = ScheduleModelFactory(session=session, class_=class_).create_and_refresh(
        allocated=True
    )
    _add_occurrence(
        session, classroom, must_be_int(schedule.id), time(14, 0), time(16, 0)
    )

    response = client.post(
        f"{URL_PREFIX}/with-conflict-count/{classroom.building_id}",
        json={
            "start_time": "15:59:00",
            "end_time": "17:59:00",
            "recurrence": Recurrence.CUSTOM.value,
            "dates": [TEST_DATE.isoformat()],
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert _conflicts_for_classroom(response.json(), must_be_int(classroom.id)) == 1


def test_get_with_conflict_count_for_schedule_does_not_flag_touching_ranges(
    classroom: Classroom, class_: Class, client: TestClient, session: Session
) -> None:
    """Same scenario as above, driven through the schedule-comparison GET
    route instead of the raw-times POST route: a candidate schedule at
    [16:00-18:00] must not conflict with an existing [14:00-16:00] booking
    in the classroom."""
    existing_schedule = ScheduleModelFactory(
        session=session, class_=class_
    ).create_and_refresh(allocated=True, start_date=TEST_DATE, end_date=TEST_DATE)
    _add_occurrence(
        session,
        classroom,
        must_be_int(existing_schedule.id),
        time(14, 0),
        time(16, 0),
    )

    candidate_schedule = ScheduleModelFactory(
        session=session, class_=class_
    ).create_and_refresh(allocated=True, start_date=TEST_DATE, end_date=TEST_DATE)
    candidate_occurrence = Occurrence(
        start_time=time(16, 0),
        end_time=time(18, 0),
        date=TEST_DATE,
        classroom_id=None,
        schedule_id=must_be_int(candidate_schedule.id),
    )
    session.add(candidate_occurrence)
    session.commit()
    session.refresh(candidate_schedule)

    response = client.get(
        f"{URL_PREFIX}/with-conflict-count/{classroom.building_id}/{candidate_schedule.id}"
    )

    assert response.status_code == status.HTTP_200_OK
    assert _conflicts_for_classroom(response.json(), must_be_int(classroom.id)) == 0
