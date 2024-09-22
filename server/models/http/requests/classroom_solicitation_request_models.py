from pydantic import BaseModel
from datetime import time, date
from server.utils.enums.reservation_type import ReservationType


class ClassroomSolicitationRegister(BaseModel):
    classroom_id: int | None = None
    building_id: int
    reason: str | None = None
    reservation_title: str
    reservation_type: ReservationType
    dates: list[date]
    start_time: time | None = None
    end_time: time | None = None
    capacity: int


class ClassroomSolicitationApprove(BaseModel):
    classroom_id: int
    classroom_name: str
    start_time: time
    end_time: time


class ClassroomSolicitationDeny(BaseModel):
    justification: str
