from enum import Enum


class ReservationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    CANCELLED = "cancelled"
    DELETED = "deleted"

    @staticmethod
    def values() -> list["ReservationStatus"]:
        return [
            ReservationStatus.CANCELLED,
            ReservationStatus.PENDING,
            ReservationStatus.APPROVED,
            ReservationStatus.DENIED,
            ReservationStatus.DELETED,
        ]

    @staticmethod
    def get_status_detail(status: "ReservationStatus") -> str:
        status_details = {
            ReservationStatus.PENDING: "A reserva está pendente.",
            ReservationStatus.APPROVED: "A reserva está aprovada.",
            ReservationStatus.DENIED: "A reserva está negada.",
            ReservationStatus.CANCELLED: "A reserva está cancelada.",
            ReservationStatus.DELETED: "A reserva está excluída.",
        }
        return status_details.get(status, "Status desconhecido.")
