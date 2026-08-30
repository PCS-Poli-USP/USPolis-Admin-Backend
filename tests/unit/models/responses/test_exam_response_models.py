from datetime import date

from server.models.http.responses.exam_response_models import (
    ExamEventResponse,
    ExamResponse,
)
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.reservation_type import ReservationType
from tests.utils.academic_test_utils import (
    make_building,
    make_class,
    make_classroom,
    make_exam,
    make_occurrence,
    make_reservation,
    make_subject,
)
from tests.utils.time_test_utils import make_schedule


class TestExamResponse:
    def test_from_exam_includes_reservation_and_classes(self) -> None:
        subject = make_subject(code="MAC0110")
        class_ = make_class(subject=subject, code="T01")
        classroom = make_classroom(building=make_building())
        schedule = make_schedule(class_=class_, classroom=classroom)
        schedule.occurrences = []
        schedule.logs = []
        reservation = make_reservation(schedule=schedule, type_=ReservationType.EXAM)
        exam = make_exam(reservation=reservation, subject=subject, classes=[class_])

        data = ExamResponse.from_exam(exam)

        assert data.reservation.id == reservation.id
        assert [c.id for c in data.classes] == [class_.id]

    def test_from_exams(self) -> None:
        subject = make_subject()
        class_ = make_class(subject=subject)
        classroom = make_classroom(building=make_building())
        schedule1 = make_schedule(class_=class_, classroom=classroom)
        schedule1.occurrences = []
        schedule1.logs = []
        reservation1 = make_reservation(schedule=schedule1, type_=ReservationType.EXAM)
        exam1 = make_exam(reservation=reservation1, subject=subject, classes=[class_])

        schedule2 = make_schedule(class_=class_, classroom=classroom)
        schedule2.occurrences = []
        schedule2.logs = []
        reservation2 = make_reservation(schedule=schedule2, type_=ReservationType.EXAM)
        exam2 = make_exam(reservation=reservation2, subject=subject, classes=[class_])

        data = ExamResponse.from_exams([exam1, exam2])

        assert [d.id for d in data] == [exam1.id, exam2.id]


class TestExamEventResponse:
    def test_from_exam_with_custom_recurrence_uses_occurrences(self) -> None:
        subject = make_subject(code="MAC0110")
        class_ = make_class(subject=subject)
        schedule = make_schedule(class_=class_, recurrence=Recurrence.CUSTOM)
        reservation = make_reservation(
            schedule=schedule, type_=ReservationType.EXAM, title="Prova"
        )
        exam = make_exam(reservation=reservation, subject=subject, classes=[class_])
        occurrence = make_occurrence(schedule=schedule, occurrence_date=date(2025, 3, 1))
        schedule.occurrences = [occurrence]

        events = ExamEventResponse.from_exam(exam)

        assert len(events) == 1
        assert events[0].id == str(exam.id)
        assert events[0].title == "Prova"
        assert events[0].extendedProps is not None
        assert events[0].extendedProps.subject_code == "MAC0110"
        assert events[0].rrule is None

    def test_from_exam_with_non_custom_recurrence_uses_schedule_rrule(self) -> None:
        subject = make_subject()
        class_ = make_class(subject=subject)
        schedule = make_schedule(class_=class_, recurrence=Recurrence.WEEKLY)
        reservation = make_reservation(
            schedule=schedule, type_=ReservationType.EXAM, title="Prova"
        )
        exam = make_exam(reservation=reservation, subject=subject, classes=[class_])

        events = ExamEventResponse.from_exam(exam)

        assert len(events) == 1
        assert events[0].rrule is not None

    def test_from_exams(self) -> None:
        subject = make_subject()
        class_ = make_class(subject=subject)
        schedule = make_schedule(class_=class_, recurrence=Recurrence.WEEKLY)
        reservation = make_reservation(schedule=schedule, type_=ReservationType.EXAM)
        exam = make_exam(reservation=reservation, subject=subject, classes=[class_])

        events = ExamEventResponse.from_exams([exam])

        assert len(events) == 1
