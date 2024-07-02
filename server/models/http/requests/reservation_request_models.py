from datetime import datetime
from pydantic import BaseModel

from server.models.http.requests.schedule_request_models import ScheduleRegister, ScheduleUpdate


class ReservationBase(BaseModel):
    name: str
    type: str
    description: str
    updated_at: datetime
    classroom_id: int


class ReservationRegister(ReservationBase):
    schedule_data: ScheduleRegister


class ReservationUpdate(ReservationBase):
    schedule_data: ScheduleUpdate
