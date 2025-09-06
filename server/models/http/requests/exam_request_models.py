from typing import Self, TypeVar, Union
from pydantic import BaseModel, model_validator
from server.models.http.requests.reservation_request_models import (
    ReservationRegister,
    ReservationUpdate,
)
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.reservation_type import ReservationType


class ExamBase(BaseModel):
    type: ReservationType = ReservationType.EXAM
    subject_id: int
    class_ids: list[int] = []
    labels: list[str]

    @model_validator(mode="after")
    def validate_body(self) -> Self:
        if not self.labels:
            raise ValueError("Labels must not be empty")
        return self


T = TypeVar("T", bound=Union["ExamRegister", "ExamUpdate"])


def validate_exam(self: T) -> T:
    data = self.schedule_data
    if data.recurrence != Recurrence.CUSTOM:
        raise ValueError("Exam must have custom recurrence")
    if not data.dates:
        raise ValueError("Exam must have an occurrence")
    if len(data.dates) != len(self.labels):
        raise ValueError("Each date must have a corresponding label")
    return self


class ExamRegister(ExamBase, ReservationRegister):
    @model_validator(mode="after")
    def validate_body(self) -> Self:
        return validate_exam(self)


class ExamUpdate(ExamBase, ReservationUpdate):
    @model_validator(mode="after")
    def validate_body(self) -> Self:
        return validate_exam(self)
