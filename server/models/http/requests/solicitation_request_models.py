from pydantic import BaseModel, Field, field_validator

from server.models.http.requests.event_request_models import EventRegister
from server.models.http.requests.exam_request_models import ExamRegister
from server.models.http.requests.meeting_request_models import MeetingRegister


class ExamSolicitation(ExamRegister):
    classroom_id: int | None = None  # type: ignore


class MeetingSolicitation(MeetingRegister):
    classroom_id: int | None = None  # type: ignore


class EventSolicitation(EventRegister):
    classroom_id: int | None = None  # type: ignore


SolicitationData = ExamSolicitation | MeetingSolicitation | EventSolicitation


class SolicitationRegister(BaseModel):
    capacity: int
    required_classroom: bool
    building_id: int
    reservation_data: SolicitationData


APPROVE_MESSAGE_MAX_LENGTH = 256


class SolicitationApprove(BaseModel):
    classroom_id: int
    classroom_name: str
    # Optional note from the approver, sent in the approval email only (not
    # stored).
    message: str | None = Field(default=None, max_length=APPROVE_MESSAGE_MAX_LENGTH)

    @field_validator("message")
    @classmethod
    def blank_message_is_none(cls, message: str | None) -> str | None:
        if message is None:
            return None
        return message.strip() or None


class SolicitationUpdated(SolicitationApprove):
    pass


class SolicitationDeleted(SolicitationRegister):
    pass


class SolicitationDeny(BaseModel):
    justification: str
