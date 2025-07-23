from enum import Enum


class SolicitationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    CANCELLED = "cancelled"
    DELETED = "deleted"

    @staticmethod
    def values() -> list["SolicitationStatus"]:
        return [
            SolicitationStatus.CANCELLED,
            SolicitationStatus.PENDING,
            SolicitationStatus.APPROVED,
            SolicitationStatus.DENIED,
            SolicitationStatus.DELETED,
        ]
