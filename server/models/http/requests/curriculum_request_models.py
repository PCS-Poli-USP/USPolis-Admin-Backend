from pydantic import BaseModel

class CurriculumRegister(BaseModel):
    course_id: int
    AAC: int
    AEX: int
    description: str

class CurriculumUpdate(BaseModel):
    course_id: int
    AAC: int
    AEX: int
    description: str
