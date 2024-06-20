from enum import Enum


class Recurrence(Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    BIWEEKLY = "Biweekly"
    MONTHLY = "Monthly"
    NONE = "None"
    CUSTOM = "Custom" # TODO: remove one of None or Custom

    def to_string(self) -> str:
        return self.value
