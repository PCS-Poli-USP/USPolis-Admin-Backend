from server.models.database.reservation_db_model import Reservation

from server.models.http.responses.event_response_models import EventResponseBase
from server.models.http.responses.exam_response_models import ExamResponseBase
from server.models.http.responses.meeting_response_models import MeetingResponseBase
from server.models.http.responses.reservation_response_base import (
    ReservationResponseBase,
)
from server.models.http.responses.schedule_response_models import (
    ScheduleResponse,
    ScheduleFullResponse,
)


class ReservationResponse(ReservationResponseBase):
    schedule: ScheduleResponse
    exam: ExamResponseBase | None = None
    meeting: MeetingResponseBase | None = None
    event: EventResponseBase | None = None

    @classmethod
    def from_reservation(cls, reservation: Reservation) -> "ReservationResponse":
        base = ReservationResponseBase.from_reservation(reservation)
        return cls(
            **base.model_dump(),
            schedule=ScheduleResponse.from_schedule(reservation.schedule),
            exam=ExamResponseBase.from_exam(reservation.exam)
            if reservation.exam
            else None,
            meeting=MeetingResponseBase.from_meeting(reservation.meeting)
            if reservation.meeting
            else None,
            event=EventResponseBase.from_event(reservation.event)
            if reservation.event
            else None,
        )

    @classmethod
    def from_reservation_list(
        cls, reservations: list[Reservation]
    ) -> list["ReservationResponse"]:
        return [cls.from_reservation(reservation) for reservation in reservations]


class ReservationFullResponse(ReservationResponseBase):
    schedule: ScheduleFullResponse

    @classmethod
    def from_reservation(cls, reservation: Reservation) -> "ReservationFullResponse":
        base = ReservationResponseBase.from_reservation(reservation)
        return cls(
            **base.model_dump(),
            schedule=ScheduleFullResponse.from_schedule(reservation.schedule),
        )

    @classmethod
    def from_reservation_list(
        cls, reservations: list[Reservation]
    ) -> list["ReservationFullResponse"]:
        return [cls.from_reservation(reservation) for reservation in reservations]
