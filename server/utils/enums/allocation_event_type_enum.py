from enum import Enum

from server.utils.enums.reservation_type import ReservationType


class AllocationEventType(str, Enum):
    SUBJECT = "subject"
    EXAM = "exam"
    EVENT = "event"
    MEETING = "meeting"

    @staticmethod
    def values() -> list["AllocationEventType"]:
        return [
            AllocationEventType.SUBJECT,
            AllocationEventType.EXAM,
            AllocationEventType.EVENT,
            AllocationEventType.MEETING,
        ]

    @staticmethod
    def get_from_reservation_type(
        reservation_type: ReservationType,
    ) -> "AllocationEventType":
        mapping = {
            ReservationType.EXAM: AllocationEventType.EXAM,
            ReservationType.EVENT: AllocationEventType.EVENT,
            ReservationType.MEETING: AllocationEventType.MEETING,
        }
        return mapping.get(reservation_type, AllocationEventType.EVENT)
