from typing import Self

from server.models.database.meeting_db_model import Meeting

from server.models.http.responses.reservation_response_base import (
    MeetingResponseBase,
    ReservationCoreResponse,
)


class MeetingResponse(MeetingResponseBase):
    reservation: ReservationCoreResponse

    @classmethod
    def from_meeting(cls, meeting: Meeting) -> Self:
        base = super().from_meeting(meeting)
        return cls(
            **base.model_dump(),
            reservation=ReservationCoreResponse.from_reservation(meeting.reservation),
        )

    @classmethod
    def from_meetings(cls, meetings: list[Meeting]) -> list[Self]:
        return [cls.from_meeting(meeting) for meeting in meetings]
