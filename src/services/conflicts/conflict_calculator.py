from src.services.conflicts.conflict_list_grouper import ConflictListGrouper
from src.services.conflicts.utils import ConflictsUtils as utils


class ConflictCalculator:
    __event1: dict = {}
    __event2: dict = {}
    __conflicts: list[dict] = []

    def __init__(self):
        self.__conflicts = []
        self.__event1 = {}
        self.__event2 = {}

    # TODO: event conflicts with itself, because it is in the events list
    @staticmethod
    def check_time_conflict_one_with_many(event: dict, events: list[dict]):
        conflict_calculator = ConflictCalculator()
        return conflict_calculator.__check_time_conflict_one_with_many(event, events)

    def __check_time_conflict_one_with_many(self, event: dict, events: list[dict]):
        for e in events:
            id1 = str(e.get("_id"))
            id2 = event.get("id")
            if str(e.get("_id")) == event.get("id"):
                continue
            self.__event1 = event
            self.__event2 = e
            if self.__check_time_conflict():
                return True
        return False

    @staticmethod
    def calculate_conflicts_list(events: list[dict]):
        conflict_calculator = ConflictCalculator()
        return conflict_calculator.__calculate_conflicts_list(events)

    def __calculate_conflicts_list(self, all_events: list[dict]):
        for i in range(len(all_events)):
            for j in range(i + 1, len(all_events)):
                self.__event2 = all_events[i]
                self.__event1 = all_events[j]
                if self.__check_conflict():
                    self.__add_conflict()
        grouped_conflicts = ConflictListGrouper.group(self.__conflicts)
        return grouped_conflicts

    def __check_conflict(self) -> bool:
        return self.__check_space_conflict() and self.__check_time_conflict()

    def __check_space_conflict(self) -> bool:
        return self.__check_building_equal() and self.__check_classroom_equal()

    def __check_time_conflict(self) -> bool:
        return self.__check_week_day_equal() and self.__check_time_overlap()

    def __check_building_equal(self):
        preferences1 = self.__event1.get("preferences")
        preferences2 = self.__event2.get("preferences")

        if preferences1 is None or preferences2 is None:
            return False

        building1 = preferences1.get("building_id")
        building2 = preferences2.get("building_id")

        return building1 == building2

    def __check_classroom_equal(self) -> bool:
        return self.__check_field_equal("classroom")

    def __check_week_day_equal(self) -> bool:
        return self.__check_field_equal("week_day")

    def __check_time_overlap(self) -> bool:
        return utils.check_time_overlap(self.__event1, self.__event2)

    def __check_field_equal(self, field: str) -> bool:
        return self.__event1.get(field) == self.__event2.get(field)

    def __add_conflict(self):
        if self.__event1 not in self.__conflicts:
            self.__conflicts.append(self.__event1)

        if self.__event2 not in self.__conflicts:
            self.__conflicts.append(self.__event2)
