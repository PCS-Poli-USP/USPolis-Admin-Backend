from enum import Enum


class ConflictType(str, Enum):
    """
    Enum representing the type of conflict.
    """

    INTENTIONAL = "intentional"
    UNINTENTIONAL = "unintentional"

    @classmethod
    def values(cls) -> list["ConflictType"]:
        """
        Returns a list of all possible values of the ConflictType enum.
        """
        return [cls.INTENTIONAL, cls.UNINTENTIONAL]


class ConflictStatus(str, Enum):
    """
    Enum representing the status of a conflict.
    """

    PENDING = "pending"
    EXPIRED = "expired"
    IGNORED = "ignored"

    @classmethod
    def values(cls) -> list["ConflictStatus"]:
        """
        Returns a list of all possible values of the ConflictStatus enum.
        """
        return [cls.PENDING, cls.EXPIRED, cls.IGNORED]
