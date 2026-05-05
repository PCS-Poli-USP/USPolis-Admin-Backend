from datetime import datetime
from pydantic import BaseModel

from server.models.database.course_db_model import Course
from server.utils.enums.course_period_type_enum import CoursePeriodType
from server.utils.must_be_int import must_be_int

class CourseResponse(BaseModel):
    id: int
    name: str
    minimal_duration: int
    ideal_duration: int
    maximal_duration: int
    updated_at: datetime
    updated_by_id: int
    created_at: datetime
    created_by_id: int
    period: CoursePeriodType

    @classmethod
    def from_course(cls, course: Course) -> "CourseResponse":
        return cls(
            id=must_be_int(course.id),
            name=course.name,
            minimal_duration=course.minimal_duration,
            ideal_duration=course.ideal_duration,
            maximal_duration=course.maximal_duration,
            updated_at=course.updated_at,
            updated_by_id=must_be_int(course.updated_by_id),
            created_at=course.created_at,
            created_by_id=must_be_int(course.created_by_id),
            period=course.period,
        )

    @classmethod
    def from_course_list(cls, courses: list[Course]) -> list["CourseResponse"]:
        return [cls.from_course(course) for course in courses]

