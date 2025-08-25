from server.models.http.requests.reservation_request_models import (
    ReservationRegister,
)
from server.utils.enums.reservation_type import ReservationType


class ExamBase(ReservationRegister):
    type: ReservationType = ReservationType.EXAM
    subject_id: int
    class_ids: list[int] = []


class ExamRegister(ExamBase):
    pass


class ExamUpdate(ExamBase):
    pass
