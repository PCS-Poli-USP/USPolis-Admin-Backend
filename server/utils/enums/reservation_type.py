from enum import Enum


class ReservationType(Enum):
    EXAM = "exam"
    MEETING = "meeting"
    EVENT = "event"
    OTHER = "other"

    @classmethod
    def from_str(cls, value: str) -> "ReservationType":
        exam_values = ["Prova"]
        meeting_values = ["Reunião"]
        event_values = ["Evento"]
        other_values = ["Outro"]

        if value in exam_values:
            return cls.EXAM
        if value in meeting_values:
            return cls.MEETING
        if value in event_values:
            return cls.EVENT
        if value in other_values:
            return cls.OTHER
        raise NoSuchReservationType(f"Reservation type {value} is not valid.")


class NoSuchReservationType(Exception):
    pass
