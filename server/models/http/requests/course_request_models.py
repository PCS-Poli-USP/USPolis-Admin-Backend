from pydantic import BaseModel

from server.utils.enums.course_period_type_enum import CoursePeriodType

class CourseRegister(BaseModel):
    name: str
    minimal_duration: int
    ideal_duration: int
    maximal_duration: int
    period: CoursePeriodType

class CourseUpdate(BaseModel):
    name: str
    minimal_duration: int
    ideal_duration: int
    maximal_duration: int
    period: CoursePeriodType
