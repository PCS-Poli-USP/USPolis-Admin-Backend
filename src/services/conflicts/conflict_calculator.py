from datetime import datetime
from itertools import groupby


class ConflictCalculator:
    # TODO: group the response by buildings, classrooms and week_days

    def __init__(self, events: list[dict]):
        self.__all_events = events

    __event1: dict = {}
    __event2: dict = {}
    __all_events: list[dict] = []
    __conflicts: list[dict] = []

    def calculate_conflicts_list(self):
        for i in range(len(self.__all_events)):
            for j in range(i + 1, len(self.__all_events)):
                self.__event2 = self.__all_events[i]
                self.__event1 = self.__all_events[j]
                if self.__check_conflict():
                    self.__add_conflict()
        grouped_result = self.__group_conflicts()
        return grouped_result

    def __group_conflicts(self) -> dict:
        result = self.__group_events_by_key(self.__conflicts, "building")
        for building in result:
            result[building] = self.__group_events_by_key(result[building], "classroom")
            for classroom in result[building]:
                # TODO: special treatment for sorting week_days,
                # its not alfabetical order
                result[building][classroom] = self.__group_events_by_key(
                    result[building][classroom], "week_day"
                )
                for week_day in result[building][classroom]:
                    result[building][classroom][week_day].sort(
                        key=lambda x: self.__parse_time(x["start_time"])
                    )
        return result

    def __group_events_by_key(self, events: list[dict], key: str) -> dict:
        events.sort(key=lambda x: x[key])
        return {
            key: list(group) for key, group in groupby(events, key=lambda x: x[key])
        }

    def __add_conflict(self):
        if self.__event1 not in self.__conflicts:
            self.__conflicts.append(self.__event1)

        if self.__event2 not in self.__conflicts:
            self.__conflicts.append(self.__event2)

    def __check_conflict(self) -> bool:
        if (
            self.__check_field_equal("building")
            and self.__check_field_equal("classroom")
            and self.__check_field_equal("week_day")
        ):
            return self.__check_time_overlap()
        return False

    def __check_time_overlap(self) -> bool:
        start_time1 = self.__parse_time(self.__event1.get("start_time"))
        end_time1 = self.__parse_time(self.__event1.get("end_time"))
        start_time2 = self.__parse_time(self.__event2.get("start_time"))
        end_time2 = self.__parse_time(self.__event2.get("end_time"))

        return (
            start_time1 <= start_time2 <= end_time1
            or start_time2 <= start_time1 <= end_time2
            or (start_time1 <= start_time2 and end_time1 >= end_time2)
            or (start_time2 <= start_time1 and end_time2 >= end_time1)
        )

    def __parse_time(self, time):
        return datetime.strptime(time, "%H:%M")

    def __check_field_equal(self, field: str) -> bool:
        return self.__event1.get(field) == self.__event2.get(field)
