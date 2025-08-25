from typing import Self
from pydantic import BaseModel

from server.models.database.meeting_db_model import Meeting
from server.models.http.responses.reservation_response_models import ReservationResponse
from server.utils.must_be_int import must_be_int


class MeetingResponse(BaseModel):
    id: int
    link: str | None
    reservation: ReservationResponse

    @classmethod
    def from_meeting(cls, meeting: Meeting) -> Self:
        return cls(
            id=must_be_int(meeting.id),
            link=meeting.link,
            reservation=ReservationResponse.from_reservation(meeting.reservation),
        )

    @classmethod
    def from_meetings(cls, meetings: list[Meeting]) -> list[Self]:
        return [cls.from_meeting(meeting) for meeting in meetings]
