from enum import Enum


class ClassType(Enum):
    PRACTIC = "practic"
    THEORIC = "theoric"
    VINCULATED_THEORIC = "vinculated_theoric"
    VINCULATED_PRACTIC = "vinculated_practic"

    @classmethod
    def from_str(cls, value: str) -> "ClassType":
        pratic_values = ["Prática"]
        teoric_values = ["Teórica"]
        vinculated_theoric_values = ["Teórica Vinculada"]
        vinculated_practic_values = ["Prática Vinculada"]
        if value in pratic_values:
            return cls.PRACTIC
        if value in teoric_values:
            return cls.THEORIC
        if value in vinculated_theoric_values:
            return cls.VINCULATED_THEORIC
        if value in vinculated_practic_values:
            return cls.VINCULATED_PRACTIC
        raise NoSuchClassType(f"Class type {value} is not valid.")

    @staticmethod
    def values() -> list["ClassType"]:
        return [
            ClassType.PRACTIC,
            ClassType.THEORIC,
            ClassType.VINCULATED_THEORIC,
            ClassType.VINCULATED_PRACTIC,
        ]


class NoSuchClassType(Exception):
    pass
