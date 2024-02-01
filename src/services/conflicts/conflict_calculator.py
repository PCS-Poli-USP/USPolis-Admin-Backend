from src.services.conflicts.conflict_list_grouper import ConflictListGrouper
from src.services.conflicts.utils import ConflictsUtils as utils


class ConflictCalculator:
    __event1: dict = {}
    __event2: dict = {}
    __all_events: list[dict] = []
    __conflicts: list[dict] = []

    @staticmethod
    def calculate_conflicts_list(events: list[dict]):
        conflict_calculator = ConflictCalculator(events)
        return conflict_calculator.__calculate_conflicts_list()

    def __init__(self, events: list[dict]):
        self.__all_events = events
        self.__conflicts = []
        self.__event1 = {}
        self.__event2 = {}

    def __calculate_conflicts_list(self):
        for i in range(len(self.__all_events)):
            for j in range(i + 1, len(self.__all_events)):
                self.__event2 = self.__all_events[i]
                self.__event1 = self.__all_events[j]
                if self.__check_conflict():
                    self.__add_conflict()
        grouped_conflicts = ConflictListGrouper.group(self.__conflicts)
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
        return utils.check_time_overlap(self.__event1, self.__event2)

    def __check_field_equal(self, field: str) -> bool:
        return self.__event1.get(field) == self.__event2.get(field)
