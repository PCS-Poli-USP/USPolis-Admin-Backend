from typing import Self
from pydantic import BaseModel

from server.models.database.exam_db_model import Exam
from server.models.database.occurrence_db_model import Occurrence
from server.models.http.responses.allocation_response_models import RRule
from server.models.http.responses.class_response_models import ClassResponseBase


from server.models.http.responses.reservation_response_base import (
    ExamResponseBase,
    ReservationCoreResponse,
)
from server.utils.enums.recurrence import Recurrence
from server.utils.must_be_int import must_be_int


class ExamResponse(ExamResponseBase):
    reservation: ReservationCoreResponse
    classes: list[ClassResponseBase]

    @classmethod
    def from_exam(cls, exam: Exam) -> Self:
        base = ExamResponseBase.from_exam(exam)
        return cls(
            **base.model_dump(),
            reservation=ReservationCoreResponse.from_reservation(exam.reservation),
            classes=[ClassResponseBase.from_class(c) for c in exam.classes],
        )

    @classmethod
    def from_exams(cls, exams: list[Exam]) -> list[Self]:
        return [cls.from_exam(exam) for exam in exams]


class ExamEventExtendedProps(BaseModel):
    subject_code: str


class ExamEventResponse(BaseModel):
    id: str
    title: str
    start: str
    end: str

    rrule: RRule | None = None
    resourceId: str | None = None
    extendedProps: ExamEventExtendedProps | None = None

    @classmethod
    def from_exam_occurrence(
        cls, exam: Exam, occurrence: Occurrence
    ) -> "ExamEventResponse":
        reservation = exam.reservation
        return cls(
            id=str(must_be_int(exam.id)),
            title=reservation.title,
            start=f"{occurrence.date}T{occurrence.start_time}",
            end=f"{occurrence.date}T{occurrence.end_time}",
            extendedProps=ExamEventExtendedProps(
                subject_code=exam.subject.code,
            ),
        )

    @classmethod
    def from_exam(cls, exam: Exam) -> list["ExamEventResponse"]:
        reservation = exam.reservation
        schedule = reservation.schedule
        if schedule.recurrence == Recurrence.CUSTOM:
            return [cls.from_exam_occurrence(exam, o) for o in schedule.occurrences]
        return [
            cls(
                id=str(must_be_int(exam.id)),
                title=reservation.title,
                start=f"{schedule.start_date}T{schedule.start_time}",
                end=f"{schedule.end_date}T{schedule.end_time}",
                rrule=RRule.from_schedule(reservation.schedule),
                extendedProps=ExamEventExtendedProps(
                    subject_code=exam.subject.code,
                ),
            )
        ]

    @classmethod
    def from_exams(cls, exams: list[Exam]) -> list["ExamEventResponse"]:
        response = []
        for exam in exams:
            response.extend(cls.from_exam(exam))
        return response
