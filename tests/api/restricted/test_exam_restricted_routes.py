from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from server.models.database.exam_db_model import Exam
from server.models.database.subject_db_model import Subject
from server.models.database.classroom_db_model import Classroom
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
