from pydantic import BaseModel
from server.models.http.requests.reservation_request_models import (
    ReservationRegister,
    ReservationUpdate,
)


class MeetingBase(BaseModel):
    link: str | None = None


class MeetingRegister(MeetingBase, ReservationRegister):
    pass


class MeetingUpdate(MeetingBase, ReservationUpdate):
    pass
