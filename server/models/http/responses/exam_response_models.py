from typing import Self
from pydantic import BaseModel

from server.models.database.exam_db_model import Exam
from server.models.http.responses.class_response_models import ClassResponse
from server.models.http.responses.reservation_response_models import ReservationResponse
from server.utils.must_be_int import must_be_int


class ExamResponse(BaseModel):
    id: int
    reservation_id: int
    subject_id: int
    subject_code: str
    subject_name: str

    reservation: ReservationResponse
    classes: list[ClassResponse]

    @classmethod
    def from_exam(cls, exam: Exam) -> Self:
        return cls(
            id=must_be_int(exam.id),
            reservation_id=must_be_int(exam.reservation_id),
            subject_id=must_be_int(exam.subject_id),
            subject_code=exam.subject.code,
            subject_name=exam.subject.name,
            reservation=ReservationResponse.from_reservation(exam.reservation),
            classes=[ClassResponse.from_class(c) for c in exam.classes],
        )

    @classmethod
    def from_exams(cls, exams: list[Exam]) -> list[Self]:
        return [cls.from_exam(exam) for exam in exams]
