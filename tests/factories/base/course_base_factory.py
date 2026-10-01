from server.models.dicts.base.course_base_dict import CourseBaseDict
from server.utils.enums.course_period_type_enum import CoursePeriodType
from tests.factories.base.base_factory import BaseFactory


class CourseBaseFactory(BaseFactory):
    def __init__(self) -> None:
        super().__init__()

    def get_base_defaults(self) -> CourseBaseDict:
        return {
            "name": self.faker.unique.job(),
            "minimal_duration": 8,
            "ideal_duration": 8,
            "maximal_duration": 14,
            "period": self.faker.random_element(CoursePeriodType.values()),
        }
