from datetime import datetime
from pydantic import BaseModel

from server.models.database.curriculum_db_model import Curriculum
from server.utils.must_be_int import must_be_int

class CurriculumResponse(BaseModel):
    id: int
    course_id: int
    AAC: int
    AEX: int
    updated_at: datetime
    updated_by_id: int
    created_at: datetime
    created_by_id: int
    description: str
    course: str | None

    @classmethod
    def from_curriculum(cls, curriculum: Curriculum) -> "CurriculumResponse":
        return cls(
            id=must_be_int(curriculum.id),
            course_id=must_be_int(curriculum.course_id),
            AAC=curriculum.AAC,
            AEX=curriculum.AEX,
            updated_at=curriculum.updated_at,
            updated_by_id=must_be_int(curriculum.updated_by_id),
            created_at=curriculum.created_at,
            created_by_id=must_be_int(curriculum.created_by_id),
            description=curriculum.description,
            course=curriculum.course.name if curriculum.course else None,
        )

    @classmethod
    def from_curriculum_list(cls, curriculums: list[Curriculum]) -> list["CurriculumResponse"]:
        return [cls.from_curriculum(curriculum) for curriculum in curriculums]

