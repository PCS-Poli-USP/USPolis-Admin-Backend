from enum import Enum


class SubjectType(str, Enum):
    BIANNUAL = "biannual"
    FOUR_MONTHLY = "four_monthly"
    POSTGRADUATE = "postgraduate"
    OTHER = "other"

    @classmethod
    def from_str(cls, value: str) -> "SubjectType":
        biannual_values = ["Semestral"]
        four_monthly_values = ["Quadrimestral"]
        pos_graduation_values = ["Pós-graduação"]
        other_values = ["Outro"]

        if value in biannual_values:
            return cls.BIANNUAL
        if value in four_monthly_values:
            return cls.FOUR_MONTHLY
        if value in other_values:
            return cls.OTHER
        if value in pos_graduation_values:
            return cls.POSTGRADUATE
        raise NoSuchSubjectType(f"Subject type {value} is not valid.")

    @staticmethod
    def values() -> list["SubjectType"]:
        return [
            SubjectType.BIANNUAL,
            SubjectType.FOUR_MONTHLY,
            SubjectType.POSTGRADUATE,
            SubjectType.OTHER,
        ]


class NoSuchSubjectType(Exception):
    pass
