from enum import Enum


class MonthWeek(str, Enum):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    LAST = -1

    @staticmethod
    def values() -> list["MonthWeek"]:
        return [
            MonthWeek.FIRST,
            MonthWeek.SECOND,
            MonthWeek.THIRD,
            MonthWeek.LAST,
        ]
