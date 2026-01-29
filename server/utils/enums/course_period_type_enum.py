from enum import Enum

class CoursePeriodType(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    INTEGRAL = "integral"

    @classmethod
    def from_str(cls, value: str) -> "CoursePeriodType":
        morning_values = ["Matutino"]
        afternoon_values = ["Vespertino"]
        evening_values = ["Noturno"]
        integral_values = ["Integral"]

        if value in morning_values:
            return cls.MORNING
        if value in afternoon_values:
            return cls.AFTERNOON
        if value in evening_values:
            return cls.EVENING
        if value in integral_values:
            return cls.INTEGRAL
        raise NoSuchCoursePeriodType(f"Course Period Type {value} is not valid.")

    @staticmethod
    def values() -> list["CoursePeriodType"]:
        return [
            CoursePeriodType.MORNING,
            CoursePeriodType.AFTERNOON,
            CoursePeriodType.EVENING,
            CoursePeriodType.INTEGRAL,
        ]
    
class NoSuchCoursePeriodType(Exception):
    pass