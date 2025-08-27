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

    @staticmethod
    def get_status_detail(status: "SolicitationStatus") -> str:
        status_details = {
            SolicitationStatus.PENDING: "A solicitação está pendente.",
            SolicitationStatus.APPROVED: "A solicitação foi aprovada.",
            SolicitationStatus.DENIED: "A solicitação foi negada.",
            SolicitationStatus.CANCELLED: "A solicitação foi cancelada.",
            SolicitationStatus.DELETED: "A solicitação foi excluída.",
        }
        return status_details.get(status, "Status desconhecido.")
