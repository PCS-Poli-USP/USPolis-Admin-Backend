from server.models.dicts.base.base_dict import BaseDict
from server.utils.enums.course_period_type_enum import CoursePeriodType


class CourseBaseDict(BaseDict, total=False):
    """Base dict for course dictionaries (requests and database)"""

    name: str
    minimal_duration: int
    ideal_duration: int
    maximal_duration: int
    period: CoursePeriodType
