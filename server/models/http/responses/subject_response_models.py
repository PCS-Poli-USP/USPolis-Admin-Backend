from datetime import datetime
from pydantic import BaseModel

from server.models.database.subject_db_model import Subject
from server.models.http.exceptions.responses_exceptions import UnfetchDataError
from server.utils.enums.subject_type import SubjectType
from server.models.http.responses.building_response_models import BuildingResponse


class SubjectResponse(BaseModel):
    id: int
    buildings: list[BuildingResponse] | None = None
    code: str
    name: str
    professors: list[str]
    type: SubjectType
    class_credit: int
    work_credit: int
    activation: datetime
    desactivation: datetime | None = None

    @classmethod
    def from_subject(cls, subject: Subject) -> "SubjectResponse":
        if subject.id is None:
            raise UnfetchDataError("Subject", "ID")
        return cls(
            id=subject.id,
            code=subject.code,
            name=subject.name,
            professors=subject.professors,
            buildings=[
                BuildingResponse.from_building(building)
                for building in subject.buildings
            ]
            if subject.buildings
            else None,
            type=subject.type,
            class_credit=subject.class_credit,
            work_credit=subject.work_credit,
            activation=subject.activation,
            desactivation=subject.desactivation if subject.desactivation else None,
        )

    @classmethod
    def from_subject_list(cls, subjects: list[Subject]) -> list["SubjectResponse"]:
        return [cls.from_subject(subject) for subject in subjects]
