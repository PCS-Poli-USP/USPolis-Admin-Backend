from pydantic import BaseModel

from server.models.database.class_db_model import Class
from server.models.database.subject_db_model import Subject
from server.models.http.responses.building_response_models import BuildingResponse
from server.utils.enums.subject_type import SubjectType
from server.utils.must_be_int import must_be_int


class SubjectResponse(BaseModel):
    id: int
    building_ids: list[int]
    buildings: list[BuildingResponse]
    classes: list[Class]
    code: str
    name: str
    professors: list[str]
    type: SubjectType
    class_credit: int
    work_credit: int

    @classmethod
    def from_subject(cls, subject: Subject) -> "SubjectResponse":
        return cls(
            id=must_be_int(subject.id),
            professors=subject.professors,
            building_ids=[
                building.id for building in subject.buildings if (building.id)
            ],
            buildings=[
                BuildingResponse.from_building(building)
                for building in subject.buildings
            ],
            classes=subject.classes,
            code=subject.code,
            name=subject.name,
            type=subject.type,
            class_credit=subject.class_credit,
            work_credit=subject.work_credit,
        )

    @classmethod
    def from_subject_list(cls, subjects: list[Subject]) -> list["SubjectResponse"]:
        return [cls.from_subject(subject) for subject in subjects]


class SubjectCrawlResponse(BaseModel):
    update: bool = False
    codes: list[str]
    failed: list[str]
    sucess: list[str]
    errors: list[str]
