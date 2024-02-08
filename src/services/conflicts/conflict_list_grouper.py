from itertools import groupby

from src.services.conflicts.utils import ConflictsUtils as utils


class ConflictListGrouper:
    __conflicts: list[dict] = []

    @staticmethod
    def group(conflict_list: list):
        conflictListGrouper = ConflictListGrouper(conflict_list)
        return conflictListGrouper.__group()

    def __init__(self, conflict_list: list):
        self.__conflicts = conflict_list

    def __group(self):
        return self.__group_conflicts()

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
        events.sort(key=lambda x: utils.parse_event_time(x.get("start_time")))
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

    def __check_time_overlap_with_many(self, events: list, event: dict) -> bool:
        for e in events:
            self.__event1 = event
            self.__event2 = e
            if not utils.check_time_overlap(self.__event1, self.__event2):
                return False
        return True
