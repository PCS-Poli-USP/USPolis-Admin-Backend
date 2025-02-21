from enum import Enum


class Recurrence(Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    BIWEEKLY = "Biweekly"
    MONTHLY = "Monthly"
    CUSTOM = "Custom"

    def to_string(self) -> str:
        return self.value
