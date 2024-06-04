from datetime import datetime
from pydantic import BaseModel

from server.models.database.subject_db_model import Subject
from server.utils.enums.subject_type import SubjectType
from server.models.http.responses.building_response_models import BuildingResponse


class SubjectResponse(BaseModel):
    id: str
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
    async def from_subject(cls, subject: Subject) -> "SubjectResponse":
        await subject.fetch_all_links()
        return cls(
            id=str(subject.id),
            code=subject.code,
            name=subject.name,
            professors=subject.professors,
            buildings=[
                await BuildingResponse.from_building(building)  # type: ignore
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
    async def from_subject_list(
        cls, subjects: list[Subject]
    ) -> list["SubjectResponse"]:
        return [await cls.from_subject(subject) for subject in subjects]
