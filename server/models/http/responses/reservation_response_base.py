from datetime import date, datetime, time
from typing import Self
from pydantic import BaseModel

from server.models.database.event_db_model import Event
from server.models.database.exam_db_model import Exam
from server.models.database.meeting_db_model import Meeting
from server.models.database.occurrence_label_db_model import OccurrenceLabel
from server.models.database.reservation_db_model import Reservation
from server.models.http.responses.schedule_response_models import ScheduleResponse
from server.utils.enums.event_type_enum import EventType
from server.utils.enums.reservation_status import ReservationStatus
from server.utils.enums.reservation_type import ReservationType
from server.utils.must_be_int import must_be_int


class ExamResponseBase(BaseModel):
    id: int
    reservation_id: int
    subject_id: int
    subject_code: str
    subject_name: str
    class_ids: list[int]
    times: list[tuple[time, time]]
    labels: list[str]
    dates: list[date]

    @classmethod
    def from_exam(cls, exam: Exam) -> Self:
        occurrences = exam.get_schedule().occurrences
        labels: list[OccurrenceLabel] = []
        for o in occurrences:
            if o.occurrence_label is None:
                raise ValueError("Occurrence label is missing for an exam occurrence.")
            labels.append(o.occurrence_label)

        return cls(
            id=must_be_int(exam.id),
            reservation_id=must_be_int(exam.reservation_id),
            subject_id=must_be_int(exam.subject_id),
            subject_code=exam.subject.code,
            subject_name=exam.subject.name,
            class_ids=[must_be_int(c.id) for c in exam.classes],
            times=[(o.start_time, o.end_time) for o in occurrences],
            labels=[o.label for o in labels],
            dates=[o.date for o in occurrences],
        )


class EventResponseBase(BaseModel):
    id: int
    reservation_id: int
    link: str | None
    type: EventType

    @classmethod
    def from_event(cls, event: Event) -> Self:
        return cls(
            id=must_be_int(event.id),
            reservation_id=event.reservation_id,
            link=event.link,
            type=event.type,
        )


class MeetingResponseBase(BaseModel):
    id: int
    link: str | None

    @classmethod
    def from_meeting(cls, meeting: Meeting) -> Self:
        return cls(
            id=must_be_int(meeting.id),
            link=meeting.link,
        )


class ReservationResponseBase(BaseModel):
    id: int
    title: str
    type: ReservationType
    reason: str | None
    updated_at: datetime

    building_id: int
    building_name: str

    classroom_id: int | None
    classroom_name: str | None

    schedule_id: int

    created_by_id: int
    created_by: str
    status: ReservationStatus

    requester: str | None
    solicitation_id: int | None

    @classmethod
    def from_reservation(cls, reservation: Reservation) -> "ReservationResponseBase":
        classroom = reservation.get_classroom()
        building = reservation.get_building()
        solicitation = reservation.solicitation
        return cls(
            id=must_be_int(reservation.id),
            title=reservation.title,
            type=reservation.type,
            reason=reservation.reason,
            updated_at=reservation.updated_at,
            building_id=must_be_int(building.id),
            building_name=building.name,
            classroom_id=must_be_int(classroom.id) if classroom else None,
            classroom_name=classroom.name if classroom else None,
            schedule_id=must_be_int(reservation.schedule.id),
            created_by_id=must_be_int(reservation.created_by_id),
            created_by=reservation.created_by.name,
            status=reservation.status,
            requester=solicitation.user.name if solicitation else None,
            solicitation_id=solicitation.id if solicitation else None,
        )


class ReservationCoreResponse(ReservationResponseBase):
    """Core reservation response without specialization responses.
    That is, it does not include exam, event or meeting responses.
    """

    schedule: ScheduleResponse

    @classmethod
    def from_reservation(cls, reservation: Reservation) -> "ReservationCoreResponse":
        base = ReservationResponseBase.from_reservation(reservation)
        return cls(
            **base.model_dump(),
            schedule=ScheduleResponse.from_schedule(reservation.schedule),
        )
