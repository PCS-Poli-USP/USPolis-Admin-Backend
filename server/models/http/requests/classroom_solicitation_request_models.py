from pydantic import BaseModel
from datetime import time, date as date_type

from server.utils.enums.reservation_type import ReservationType


class ClassroomSolicitationRegister(BaseModel):
    classroom_id: int
    building_id: int
    reason: str
    reservation_type: ReservationType
    email: str
    date: date_type
    start_time: time
    end_time: time
    capacity: int


class ClassroomSolicitationUpdate(BaseModel):
    id: int
