from pydantic import BaseModel


class CourseOption(BaseModel):
    codcur: int
    codhab: int
    name: str