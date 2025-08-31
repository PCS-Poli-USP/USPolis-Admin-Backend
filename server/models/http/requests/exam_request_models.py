from pydantic import BaseModel
from server.models.http.requests.reservation_request_models import (
    ReservationRegister,
    ReservationUpdate,
)
from server.utils.enums.reservation_type import ReservationType


class ExamBase(BaseModel):
    type: ReservationType = ReservationType.EXAM
    subject_id: int
    class_ids: list[int] = []


class ExamRegister(ExamBase, ReservationRegister):
    pass


class ExamUpdate(ExamBase, ReservationUpdate):
    pass
