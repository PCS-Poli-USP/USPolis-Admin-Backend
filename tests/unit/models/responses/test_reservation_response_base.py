from datetime import date

from server.models.http.responses.reservation_response_base import (
    EventResponseBase,
    ExamResponseBase,
    MeetingResponseBase,
    ReservationCoreResponse,
    ReservationResponseBase,
)
from server.utils.enums.event_type_enum import EventType
from server.utils.enums.reservation_status import ReservationStatus
from server.utils.enums.reservation_type import ReservationType
from tests.utils.academic_test_utils import (
    make_building,
    make_class,
    make_classroom,
    make_event,
    make_exam,
    make_meeting,
    make_occurrence,
    make_reservation,
    make_solicitation,
    make_subject,
    make_user,
)
from tests.utils.time_test_utils import make_schedule


class TestExamResponseBase:
    def test_from_exam_with_occurrences_and_labels(self) -> None:
        subject = make_subject(code="MAC0110", name="Introdução à Computação")
        class_ = make_class(subject=subject)
        schedule = make_schedule(class_=class_)
        reservation = make_reservation(schedule=schedule, type_=ReservationType.EXAM)
        exam = make_exam(reservation=reservation, subject=subject, classes=[class_])
        occurrence = make_occurrence(
            schedule=schedule, occurrence_date=date(2025, 3, 1), label="Prova 1"
        )
        schedule.occurrences = [occurrence]

        data = ExamResponseBase.from_exam(exam)

        assert data.id == exam.id
        assert data.subject_id == subject.id
        assert data.subject_code == "MAC0110"
        assert data.class_ids == [class_.id]
        assert data.times == [(occurrence.start_time, occurrence.end_time)]
        assert data.labels == ["Prova 1"]
        assert data.dates == [date(2025, 3, 1)]

    def test_from_exam_occurrence_without_label(self) -> None:
        subject = make_subject()
        class_ = make_class(subject=subject)
        schedule = make_schedule(class_=class_)
        reservation = make_reservation(schedule=schedule, type_=ReservationType.EXAM)
        exam = make_exam(reservation=reservation, subject=subject, classes=[class_])
        occurrence = make_occurrence(schedule=schedule, label=None)
        schedule.occurrences = [occurrence]

        data = ExamResponseBase.from_exam(exam)

        assert data.labels == ["NAO ENCONTRADA"]


class TestEventResponseBase:
    def test_from_event(self) -> None:
        schedule = make_schedule()
        reservation = make_reservation(schedule=schedule, type_=ReservationType.EVENT)
        event = make_event(reservation=reservation, link="https://x.com", type_=EventType.TALK)

        data = EventResponseBase.from_event(event)

        assert data.id == event.id
        assert data.reservation_id == reservation.id
        assert data.link == "https://x.com"
        assert data.type == EventType.TALK


class TestMeetingResponseBase:
    def test_from_meeting(self) -> None:
        schedule = make_schedule()
        reservation = make_reservation(schedule=schedule, type_=ReservationType.MEETING)
        meeting = make_meeting(reservation=reservation, link="https://meet.com")

        data = MeetingResponseBase.from_meeting(meeting)

        assert data.id == meeting.id
        assert data.link == "https://meet.com"


class TestReservationResponseBase:
    def test_from_reservation_with_a_classroom(self) -> None:
        building = make_building(name="Bloco A")
        classroom = make_classroom(building=building, name="Sala 1")
        schedule = make_schedule(classroom=classroom)
        creator = make_user()
        reservation = make_reservation(
            schedule=schedule, created_by=creator, title="Reunião"
        )

        data = ReservationResponseBase.from_reservation(reservation)

        assert data.id == reservation.id
        assert data.title == "Reunião"
        assert data.building_id == building.id
        assert data.building_name == "Bloco A"
        assert data.classroom_id == classroom.id
        assert data.classroom_name == "Sala 1"
        assert data.schedule_id == schedule.id
        assert data.created_by_id == creator.id
        assert data.created_by == creator.name
        assert data.status == ReservationStatus.APPROVED
        assert data.requester is None
        assert data.solicitation_id is None

    def test_from_reservation_without_classroom_falls_back_to_solicitation(self) -> None:
        building = make_building(name="Bloco B")
        user = make_user()
        solicitation = make_solicitation(building=building, user=user)
        schedule = make_schedule(classroom=None)
        reservation = make_reservation(schedule=schedule, solicitation=solicitation)

        data = ReservationResponseBase.from_reservation(reservation)

        assert data.building_id == building.id
        assert data.classroom_id is None
        assert data.classroom_name is None
        assert data.requester == user.name
        assert data.solicitation_id == solicitation.id


class TestReservationCoreResponse:
    def test_from_reservation_includes_schedule(self) -> None:
        classroom = make_classroom(building=make_building())
        schedule = make_schedule(classroom=classroom)
        schedule.occurrences = []
        schedule.logs = []
        reservation = make_reservation(schedule=schedule)

        data = ReservationCoreResponse.from_reservation(reservation)

        assert data.schedule.id == schedule.id
