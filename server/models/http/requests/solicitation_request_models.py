from pydantic import BaseModel

from server.models.http.requests.event_request_models import EventRegister
from server.models.http.requests.exam_request_models import ExamRegister
from server.models.http.requests.meeting_request_models import MeetingRegister


class ExamSolicitation(ExamRegister):
    classroom_id: int | None = None  # type: ignore


class MeetingSolicitation(MeetingRegister):
    classroom_id: int | None = None  # type: ignore


class EventSolicitation(EventRegister):
    classroom_id: int | None = None # type: ignore


SolicitationData = ExamSolicitation | MeetingSolicitation | EventSolicitation


class SolicitationRegister(BaseModel):
    capacity: int
    required_classroom: bool
    building_id: int
    reservation_data: SolicitationData


class SolicitationApprove(BaseModel):
    classroom_id: int
    classroom_name: str


class SolicitationUpdated(SolicitationApprove):
    pass


class SolicitationDeleted(SolicitationRegister):
    pass


class SolicitationDeny(BaseModel):
    justification: str
