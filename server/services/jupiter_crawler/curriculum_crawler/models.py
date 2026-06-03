from pydantic import BaseModel

class CurriculumGeneralInfo(BaseModel):
    course_name: str
    minimal_duration: int
    ideal_duration: int
    maximal_duration: int
    AAC: int
    AEX: int
    habilitation_number: int
    specific_info_text: str


class CurriculumSubjectInfo(BaseModel):
    subject_code: str
    subject_name: str
    period: int