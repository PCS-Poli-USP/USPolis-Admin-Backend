from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.exam_db_model import Exam
from server.models.database.subject_db_model import Subject

URL_PREFIX = "/reservations/exams"


def _allocate_exam_classroom(exam: Exam, classroom: Classroom, session: Session) -> None:
    # ExamModelFactory/ReservationModelFactory never actually wire the
    # classroom they're given onto the created schedule, so the fixture
    # exam has no classroom/building - required for get_building() to
    # resolve when building the response.
    exam.reservation.schedule.classroom = classroom
    session.add(exam.reservation.schedule)
    session.commit()


class TestGetAllExams:
    def test_returns_exams_active_today_by_default(
        self, public_client: TestClient, exam: Exam, classroom: Classroom, session: Session
    ) -> None:
        _allocate_exam_classroom(exam, classroom, session)

        response = public_client.get(URL_PREFIX)

        assert response.status_code == status.HTTP_200_OK
        assert exam.id in [e["id"] for e in response.json()]

    def test_excludes_exams_outside_the_start_end_interval(
        self, public_client: TestClient, exam: Exam, classroom: Classroom, session: Session
    ) -> None:
        _allocate_exam_classroom(exam, classroom, session)

        response = public_client.get(
            URL_PREFIX, params={"start": "1999-01-01", "end": "1999-12-31"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert exam.id not in [e["id"] for e in response.json()]


class TestGetAllExamEvents:
    def test_returns_exam_events(
        self, public_client: TestClient, exam: Exam, classroom: Classroom, session: Session
    ) -> None:
        _allocate_exam_classroom(exam, classroom, session)

        response = public_client.get(f"{URL_PREFIX}/events")

        assert response.status_code == status.HTTP_200_OK
        assert str(exam.id) in [e["id"] for e in response.json()]


class TestGetAllSubjectExams:
    def test_returns_exams_of_the_given_subject(
        self,
        public_client: TestClient,
        exam: Exam,
        classroom: Classroom,
        subject: Subject,
        session: Session,
    ) -> None:
        _allocate_exam_classroom(exam, classroom, session)

        response = public_client.get(f"{URL_PREFIX}/subjects/{subject.id}")

        assert response.status_code == status.HTTP_200_OK
        assert exam.id in [e["id"] for e in response.json()]

    def test_returns_empty_for_a_subject_with_no_exams(
        self, public_client: TestClient, exam: Exam
    ) -> None:
        response = public_client.get(f"{URL_PREFIX}/subjects/999999")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []


class TestGetAllClassExams:
    def test_returns_exams_of_the_given_class(
        self,
        public_client: TestClient,
        exam: Exam,
        classroom: Classroom,
        class_: Class,
        session: Session,
    ) -> None:
        _allocate_exam_classroom(exam, classroom, session)
        exam.classes = [class_]
        session.add(exam)
        session.commit()

        response = public_client.get(f"{URL_PREFIX}/classes/{class_.id}")

        assert response.status_code == status.HTTP_200_OK
        assert exam.id in [e["id"] for e in response.json()]

    def test_returns_empty_for_a_class_with_no_exams(
        self, public_client: TestClient, exam: Exam
    ) -> None:
        response = public_client.get(f"{URL_PREFIX}/classes/999999")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
