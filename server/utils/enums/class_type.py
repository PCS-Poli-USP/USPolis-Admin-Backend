from enum import Enum
from typing import Self


class ClassType(Enum):
    PRACTIC = "practic"
    THEORIC = "theoric"

    @classmethod
    def from_str(cls, value: str) -> "ClassType":
        pratic_values = ["Prática"]
        teoric_values = ["Teórica"]
        if value in pratic_values:
            return cls.PRACTIC
        if value in teoric_values:
            return cls.THEORIC
        raise NoSuchClassType(f"Class type {value} is not valid.")


class NoSuchClassType(Exception):
    pass
