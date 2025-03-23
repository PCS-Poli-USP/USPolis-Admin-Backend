from enum import Enum


class ActionType(Enum):
    ALLOCATE = "allocate"
    DEALLOCATE = "deallocate"

    @classmethod
    def from_str(cls, value: str) -> "ActionType":
        allocate_values = ["Alocar"]
        deallocate_values = ["Desalocar"]

        if value in allocate_values:
            return cls.ALLOCATE
        if value in deallocate_values:
            return cls.DEALLOCATE
        raise NoSuchActionType(f"Action type {value} is not valid.")


class NoSuchActionType(Exception):
    pass
