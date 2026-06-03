from typing import List
from pydantic import BaseModel

class CurriculumRegister(BaseModel):
    course_id: int
    codcur: int
    codhab: int
    AAC: int
    AEX: int
    description: str

class CurriculumUpdate(BaseModel):
    course_id: int
    codcur: int
    codhab: int
    AAC: int
    AEX: int
    description: str

class CreateCurriculumByJupiterRequest(BaseModel):
    course_id: int
    codcur: int
    codhab: int
    description: str

class CurriculumSubjectPreview(BaseModel):
    subject_code: str
    subject_name: str
    period: int

class CreateCurriculumByJupiterFinalRequest(BaseModel):
    course_id: int
    codcur: int
    codhab: int
    description: str
    AAC: int
    AEX: int
    mandatory: List[CurriculumSubjectPreview]
    free: List[CurriculumSubjectPreview]
    elective: List[CurriculumSubjectPreview]