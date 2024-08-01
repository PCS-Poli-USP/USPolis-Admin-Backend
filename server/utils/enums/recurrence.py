from enum import Enum


class Recurrence(Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    BIWEEKLY = "Biweekly"
    MONTHLY = "Monthly"
    NONE = "None"  # TODO: remove none
    CUSTOM = "Custom"

    def to_string(self) -> str:
        return self.value
