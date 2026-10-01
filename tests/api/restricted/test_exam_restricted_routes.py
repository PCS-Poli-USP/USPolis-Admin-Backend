from datetime import date, time

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from server.models.database.exam_db_model import Exam
from server.models.database.subject_db_model import Subject
from server.models.database.classroom_db_model import Classroom
from server.utils.enums.recurrence import Recurrence
from tests.factories.request.exam_request_factory import ExamRequestFactory
from tests.utils.validators.exam.exam_model_validator import ExamModelAsserts

URL_PREFIX = "/reservations/exams"


def test_create_exam_with_admin_user(
    subject: Subject, classroom: Classroom, client: TestClient, session: Session
) -> None:
    request_factory = ExamRequestFactory(subject=subject, classroom=classroom)
    input = request_factory.create_input()
    body = jsonable_encoder(input)

    response = client.post(f"{URL_PREFIX}", json=body)

    assert response.status_code == status.HTTP_201_CREATED

    exams = list(session.exec(select(Exam)).all())
    assert len(exams) == 1

    exam = exams[0]
    ExamModelAsserts.assert_exam_after_create(exam, input)


def test_create_exam_with_restricted_user(
    subject: Subject,
    classroom: Classroom,
    restricted_client: TestClient,
    session: Session,
) -> None:
    request_factory = ExamRequestFactory(subject=subject, classroom=classroom)
    input = request_factory.create_input()
    body = jsonable_encoder(input)

    response = restricted_client.post(f"{URL_PREFIX}", json=body)

    assert response.status_code == status.HTTP_201_CREATED

    exams = list(session.exec(select(Exam)).all())
    assert len(exams) == 1

    exam = exams[0]
    ExamModelAsserts.assert_exam_after_create(exam, input)


def test_create_exam_with_common_user(common_client: TestClient) -> None:
    response = common_client.post(f"{URL_PREFIX}", json={})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_exam_with_public_user(public_client: TestClient) -> None:
    response = public_client.post(f"{URL_PREFIX}", json={})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_exam_with_distinct_times_per_date_keeps_each_occurrence_time(
    subject: Subject, classroom: Classroom, client: TestClient, session: Session
) -> None:
    """Regression test for a reported bug: an exam with two sessions at
    different times ([24/06 15:50-16:40] and [01/07 16:50-18:00]) was
    rendering both calendar events with the first session's time. Each
    Occurrence must keep its own start_time/end_time, and the schedule's own
    (single) start_time/end_time must be the envelope over every occurrence
    (min of starts, max of ends) — not an arbitrary single value — since it's
    used as a summary for the whole reservation (see
    server.models.http.responses.allocation_response_models.BaseExtendedData)."""
    request_factory = ExamRequestFactory(subject=subject, classroom=classroom)
    input = request_factory.create_input()

    first_date = date(2026, 6, 24)
    second_date = date(2026, 7, 1)
    input.schedule_data.recurrence = Recurrence.CUSTOM
    input.schedule_data.start_date = first_date
    input.schedule_data.end_date = second_date
    input.schedule_data.week_day = None
    input.schedule_data.dates = [first_date, second_date]
    input.schedule_data.times = [
        (time(15, 50), time(16, 40)),
        (time(16, 50), time(18, 0)),
    ]

    body = jsonable_encoder(input)
    response = client.post(f"{URL_PREFIX}", json=body)
    assert response.status_code == status.HTTP_201_CREATED

    exam = session.exec(select(Exam)).one()
    schedule = exam.reservation.schedule

    occurrences_by_date = {occ.date: occ for occ in schedule.occurrences}
    assert occurrences_by_date[first_date].start_time == time(15, 50)
    assert occurrences_by_date[first_date].end_time == time(16, 40)
    assert occurrences_by_date[second_date].start_time == time(16, 50)
    assert occurrences_by_date[second_date].end_time == time(18, 0)

    # Schedule-level summary must be the envelope, not either occurrence's
    # individual time.
    assert schedule.start_time == time(15, 50)
    assert schedule.end_time == time(18, 0)


def test_update_exam_with_admin_user(
    exam: Exam,
    subject: Subject,
    classroom: Classroom,
    client: TestClient,
    session: Session,
) -> None:
    request_factory = ExamRequestFactory(subject, classroom)
    input = request_factory.update_input()
    body = jsonable_encoder(input)

    response = client.put(f"{URL_PREFIX}/{exam.id}", json=body)

    assert response.status_code == status.HTTP_200_OK

    exams = list(session.exec(select(Exam)).all())
    assert len(exams) == 1

    exam = exams[0]
    ExamModelAsserts.assert_exam_after_update(exam, input)


def test_update_exam_with_restricted_user(
    exam: Exam,
    subject: Subject,
    classroom: Classroom,
    restricted_client: TestClient,
    session: Session,
) -> None:
    request_factory = ExamRequestFactory(subject, classroom)
    input = request_factory.update_input()
    body = jsonable_encoder(input)

    response = restricted_client.put(f"{URL_PREFIX}/{exam.id}", json=body)

    assert response.status_code == status.HTTP_200_OK

    exams = list(session.exec(select(Exam)).all())
    assert len(exams) == 1

    exam = exams[0]
    ExamModelAsserts.assert_exam_after_update(exam, input)


def test_update_exam_with_common_user(common_client: TestClient) -> None:
    response = common_client.put(f"{URL_PREFIX}/1", json={})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_exam_with_public_user(public_client: TestClient) -> None:
    response = public_client.put(f"{URL_PREFIX}/1", json={})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
