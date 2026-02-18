from pydantic import BaseModel

from server.utils.enums.curriculum_subject_type_enum import CurriculumSubjectType

class CurriculumSubjectRegister(BaseModel):
    curriculum_id: int
    subject_id: int
    type: CurriculumSubjectType
    period: int

class CurriculumSubjectUpdate(BaseModel):
    curriculum_id: int
    subject_id: int
    type: CurriculumSubjectType
    period: int
