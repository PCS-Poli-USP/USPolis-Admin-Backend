from enum import Enum


class WeekDay(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

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

    @classmethod
    def from_long_str(cls, day_str: str) -> "WeekDay":
        mapping = {
            "segunda": cls.MONDAY,
            "terça": cls.TUESDAY,
            "quarta": cls.WEDNESDAY,
            "quinta": cls.THURSDAY,
            "sexta": cls.FRIDAY,
            "sábado": cls.SATURDAY,
            "domingo": cls.SUNDAY,
        }
        result: WeekDay | None = mapping.get(day_str.lower())
        if result is None:
            raise NoSuchWeekDay(
                f"No such week day: {day_str}. Valid week days: {mapping.keys()}"
            )
        return result

    @classmethod
    def to_str(cls, value: int) -> str:
        dayOfWeek = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]
        return dayOfWeek[value]

    @classmethod
    def to_rrule(cls, value: int) -> str:
        dayOfWeek = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
        return dayOfWeek[value]

    @staticmethod
    def values() -> list["WeekDay"]:
        return [
            WeekDay.MONDAY,
            WeekDay.TUESDAY,
            WeekDay.WEDNESDAY,
            WeekDay.THURSDAY,
            WeekDay.FRIDAY,
            WeekDay.SATURDAY,
            WeekDay.SUNDAY,
        ]


class NoSuchWeekDay(Exception):
    pass
