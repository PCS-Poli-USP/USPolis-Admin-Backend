from enum import Enum


class CurriculumSubjectCategory(str, Enum):
    MANDATORY = "mandatory"
    FREE_ELECTIVE = "free_elective"
    TRACK_ELECTIVE = "track_elective"

    @classmethod
    def from_str(cls, value: str) -> "CurriculumSubjectCategory":
        mandatory_values = ["Obrigatória"]
        free_elective_values = ["Optativa Livre"]
        track_elective_values = ["Optativa Eletiva"]

        if value in mandatory_values:
            return cls.MANDATORY
        if value in free_elective_values:
            return cls.FREE_ELECTIVE
        if value in track_elective_values:
            return cls.TRACK_ELECTIVE
        raise NoSuchCurriculumSubjectCategory(
            f"Curriculum Subject Category {value} is not valid."
        )

    @staticmethod
    def values() -> list["CurriculumSubjectCategory"]:
        return [
            CurriculumSubjectCategory.MANDATORY,
            CurriculumSubjectCategory.FREE_ELECTIVE,
            CurriculumSubjectCategory.TRACK_ELECTIVE,
        ]


class NoSuchCurriculumSubjectCategory(Exception):
    pass
