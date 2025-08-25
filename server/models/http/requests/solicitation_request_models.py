from pydantic import BaseModel

from server.models.http.requests.event_request_models import EventRegister
from server.models.http.requests.exam_request_models import ExamRegister
from server.models.http.requests.meeting_request_models import MeetingRegister

ReservatioData = ExamRegister | MeetingRegister | EventRegister


class SolicitationRegister(BaseModel):
    capacity: int
    required_classroom: bool
    building_id: int
    reservation_data: ReservatioData


class SolicitationApprove(BaseModel):
    classroom_id: int
    classroom_name: str


class SolicitationUpdated(SolicitationApprove):
    pass


class SolicitationDeleted(SolicitationRegister):
    pass


class SolicitationDeny(BaseModel):
    justification: str
