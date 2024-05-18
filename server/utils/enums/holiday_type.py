from enum import Enum


class HolidayType(Enum):
    NATIONAL = "national"
    USP = "usp"
    EXAM = "exam"
    OTHER = "other"

    @classmethod
    def from_str(cls, value: str) -> "HolidayType":
        national_values = ["Nacional"]
        usp_values = ["Usp"]
        exam_values = ["Prova"]
        other_values = ["Outro"]

        if value in national_values:
            return cls.NATIONAL
        if value in usp_values:
            return cls.USP
        if value in exam_values:
            return cls.EXAM
        if value in other_values:
            return cls.OTHER
        raise NoSuchHolidayType(f"Holiday type {value} is not valid.")


class NoSuchHolidayType(Exception):
    pass
