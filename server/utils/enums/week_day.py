from enum import Enum


class WeekDay(Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thurday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"

    @classmethod
    def from_str(cls, day_str: str) -> "WeekDay":
        mapping = {
            "seg": cls.MONDAY,
            "ter": cls.TUESDAY,
            "qua": cls.WEDNESDAY,
            "qui": cls.THURSDAY,
            "sex": cls.FRIDAY,
            "sab": cls.SATURDAY,
            "dom": cls.SUNDAY,
        }
        result: WeekDay | None = mapping.get(day_str.lower())
        if result is None:
            raise NoSuchWeekDay(
                f"No such week day: {day_str}. Valid week days: {mapping.keys()}"
            )
        return result


class NoSuchWeekDay(Exception):
    pass
