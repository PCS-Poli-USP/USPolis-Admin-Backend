from datetime import datetime
from itertools import groupby


class ConflictCalculator:
    def __init__(self, events: list[dict]):
        self.__all_events = events
        self.__conflicts = []
        self.__event1 = {}
        self.__event2 = {}

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
        grouped_conflicts = self.__group_conflicts()
        return grouped_conflicts

    def __check_conflict(self) -> bool:
        if (
            self.__check_field_equal("building")
            and self.__check_field_equal("classroom")
            and self.__check_field_equal("week_day")
        ):
            return self.__check_time_overlap()
        return False

    def __add_conflict(self):
        if self.__event1 not in self.__conflicts:
            self.__conflicts.append(self.__event1)

        if self.__event2 not in self.__conflicts:
            self.__conflicts.append(self.__event2)

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

    def __check_time_overlap_with_many(self, events: list, event: dict) -> bool:
        for e in events:
            self.__event1 = event
            self.__event2 = e
            if not self.__check_time_overlap():
                return False
        return True

    def __group_conflicts(self) -> dict:
        self.__conflicts.sort(key=lambda x: x["building"])
        grouped_building_data = self.__group_events_by_key(self.__conflicts, "building")
        result = {}
        buildings_list = []
        for building, building_data in grouped_building_data.items():
            result = {"buildings": []}
            grouped_classroom_data = self.__group_events_by_key(
                building_data, "classroom"
            )
            classrooms_list = []
            for classroom, classroom_data in grouped_classroom_data.items():
                grouped_week_day_data = self.__group_events_by_key(
                    classroom_data, "week_day"
                )
                week_days_list = []
                for week_day, week_day_data in grouped_week_day_data.items():
                    week_day_data = self.__group_events_by_time(week_day_data)
                    week_days_list.append({"name": week_day, "events": week_day_data})
                classrooms_list.append({"name": classroom, "week_days": week_days_list})
            buildings_list.append({"name": building, "classrooms": classrooms_list})
        result = {"buildings": buildings_list}
        return result

    def __group_events_by_key(self, events: list[dict], key: str) -> dict:
        if key == "week_day":
            events.sort(key=lambda x: self.__week_day_sort_key(x[key]))
        else:
            events.sort(key=lambda x: x[key])
        return {
            key: list(group) for key, group in groupby(events, key=lambda x: x[key])
        }

    def __group_events_by_time(self, events: list[dict]) -> list:
        result = []
        events.sort(key=lambda x: self.__parse_time(x.get("start_time")))
        group = []
        for index, event in enumerate(events):
            if index == 0:
                group.append(event)
                continue
            if self.__check_time_overlap_with_many(group, event):
                group.append(event)
            else:
                result.append(group)
                group = [event]
        result.append(group)
        return result

    def __parse_time(self, time):
        return datetime.strptime(time, "%H:%M")

    def __check_field_equal(self, field: str) -> bool:
        return self.__event1.get(field) == self.__event2.get(field)

    def __week_day_sort_key(self, week_day: str) -> int:
        week_days: dict[str, int] = {
            "seg": 1,
            "ter": 2,
            "qua": 3,
            "qui": 4,
            "sex": 5,
            "sab": 6,
            "dom": 7,
        }
        index = week_days.get(week_day)
        if not index:
            return 8
        return index
