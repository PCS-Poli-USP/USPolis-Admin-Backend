from enum import Enum


class SubjectType(Enum):
    BIANNUAL = "biannual"
    FOUR_MONTHLY = "four_monthly"
    OTHER = "other"

    @classmethod
    def from_str(cls, value: str) -> "SubjectType":
        biannual_values = ["Semestral"]
        four_monthly_values = ["Quadrimestral"]
        other_values = ["Outro"]

        if value in biannual_values:
            return cls.BIANNUAL
        if value in four_monthly_values:
            return cls.FOUR_MONTHLY
        if value in other_values:
            return cls.OTHER
        raise NoSuchSubjectType(f"Subject type {value} is not valid.")


class NoSuchSubjectType(Exception):
    pass
