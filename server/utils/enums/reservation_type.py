from enum import Enum


class ReservationType(str, Enum):
    EXAM = "exam"
    MEETING = "meeting"
    EVENT = "event"

    @classmethod
    def from_str(cls, value: str) -> "ReservationType":
        exam_values = ["Prova"]
        meeting_values = ["Reunião"]
        event_values = ["Evento"]

        if value in exam_values:
            return cls.EXAM
        if value in meeting_values:
            return cls.MEETING
        if value in event_values:
            return cls.EVENT
        raise NoSuchReservationType(f"Reservation type {value} is not valid.")

    @classmethod
    def to_str(cls, value: "ReservationType") -> str:
        match value:
            case ReservationType.EXAM:
                return "Prova"
            case ReservationType.MEETING:
                return "Reunião"
            case ReservationType.EVENT:
                return "Evento"

    @classmethod
    def values(cls) -> list["ReservationType"]:
        return [
            ReservationType.EXAM,
            ReservationType.MEETING,
            ReservationType.EVENT,
        ]

    @classmethod
    def get_color(cls, value: "ReservationType") -> str:
        match value:
            case ReservationType.EXAM:
                return "#1b3b3b"
            case ReservationType.MEETING:
                return "#15584D"
            case ReservationType.EVENT:
                return "#019d94"


class NoSuchReservationType(Exception):
    pass
