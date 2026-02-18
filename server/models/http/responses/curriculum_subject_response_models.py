from pydantic import BaseModel

from server.models.database.curriculum_subject_db_model import CurriculumSubject
from server.utils.enums.curriculum_subject_type_enum import CurriculumSubjectType
from server.utils.must_be_int import must_be_int

class CurriculumSubjectResponse(BaseModel):
    id: int
    curriculum_id: int
    subject_id: int
    type: CurriculumSubjectType
    period: int
    subject_code: str | None

    @classmethod
    def from_curriculum_subject(cls, curriculum_subject: CurriculumSubject) -> "CurriculumSubjectResponse":
        return cls(
            id=must_be_int(curriculum_subject.id),
            curriculum_id=must_be_int(curriculum_subject.curriculum_id),
            subject_id=must_be_int(curriculum_subject.subject_id),
            type=curriculum_subject.type,
            period=curriculum_subject.period,
            subject_code=curriculum_subject.subject.code if curriculum_subject.subject else None,
        )

    @classmethod
    def from_curriculum_subject_list(cls, curriculum_subjects: list[CurriculumSubject]) -> list["CurriculumSubjectResponse"]:
        return [cls.from_curriculum_subject(curriculum_subject) for curriculum_subject in curriculum_subjects]

