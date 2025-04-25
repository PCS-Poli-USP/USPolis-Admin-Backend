from enum import Enum


class Recurrence(Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    BIWEEKLY = "Biweekly"
    MONTHLY = "Monthly"
    CUSTOM = "Custom"

    def to_string(self) -> str:
        return self.value

    @staticmethod
    def values() -> list["Recurrence"]:
        return [
            Recurrence.DAILY,
            Recurrence.WEEKLY,
            Recurrence.BIWEEKLY,
            Recurrence.MONTHLY,
            Recurrence.CUSTOM,
        ]
