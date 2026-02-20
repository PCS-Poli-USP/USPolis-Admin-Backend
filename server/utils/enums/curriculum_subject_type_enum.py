from enum import Enum


class CurriculumSubjectType(str, Enum):
    SEMESTRAL = "semestral"
    QUADRIMESTER = "quadrimester"

    @classmethod
    def from_str(cls, value: str) -> "CurriculumSubjectType":
        semestral_values = ["Semestral"]
        quarter_values = ["Quadrimestral"]

        if value in semestral_values:
            return cls.SEMESTRAL
        if value in quarter_values:
            return cls.QUADRIMESTER
        raise NoSuchCurriculumSubjectType(
            f"Curriculum Subject Type {value} is not valid."
        )

    @staticmethod
    def values() -> list["CurriculumSubjectType"]:
        return [
            CurriculumSubjectType.SEMESTRAL,
            CurriculumSubjectType.QUADRIMESTER,
        ]


class NoSuchCurriculumSubjectType(Exception):
    pass
