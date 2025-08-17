from enum import Enum


class EventType(str, Enum):
    TALK = "talk"
    WORKSHOP = "workshop"
    SELECTION_PROCESS = "selection_process"
    OTHER = "other"

    @classmethod
    def from_str(cls, value: str) -> "EventType":
        talk_values = ["Palestra"]
        workshop_values = ["Workshop"]
        selection_process_values = ["Processo Seletivo"]
        other_values = ["Outro"]

        if value in talk_values:
            return cls.TALK
        if value in workshop_values:
            return cls.WORKSHOP
        if value in selection_process_values:
            return cls.SELECTION_PROCESS
        if value in other_values:
            return cls.OTHER

        raise NoSuchEventType(f"Event type {value} is not valid.")

    @staticmethod
    def values() -> list["EventType"]:
        return [
            EventType.TALK,
            EventType.WORKSHOP,
            EventType.SELECTION_PROCESS,
            EventType.OTHER,
        ]


class NoSuchEventType(Exception):
    pass
