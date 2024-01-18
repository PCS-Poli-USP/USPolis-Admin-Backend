from datetime import datetime


class ConflictCalculator:
    def __init__(self, events: list[dict]):
        self.__all_events = events

    __event_to_be_compared: dict = {}
    __event_to_compare: dict = {}
    __all_events: list[dict] = []
    __conflicts: list[list[dict]] = []

    def calculate_conflicts_list(self) -> list[list[dict]]:
        for i in range(len(self.__all_events)):
            for j in range(i + 1, len(self.__all_events)):
                self.__event_to_compare = self.__all_events[i]
                self.__event_to_be_compared = self.__all_events[j]
                if self.__check_conflict():
                    self.__add_conflict()
        return self.__conflicts

    def __add_conflict(self):
        if self.__conflicts == []:
            self.__conflicts.append(
                [self.__event_to_be_compared, self.__event_to_compare]
            )
        else:
            for conflict in self.__conflicts:
                if (
                    self.__event_to_be_compared in conflict
                    or self.__event_to_compare in conflict
                ):
                    conflict.append(self.__event_to_be_compared)
                    conflict.append(self.__event_to_compare)
                    break
                else:
                    self.__conflicts.append(
                        [self.__event_to_be_compared, self.__event_to_compare]
                    )

    def __check_conflict(self) -> bool:
        if (
            self.__check_field_equal("building")
            and self.__check_field_equal("classroom")
            and self.__check_field_equal("week_day")
        ):
            start_time1 = self.__parse_time(
                self.__event_to_be_compared.get("start_time")
            )
            end_time1 = self.__parse_time(self.__event_to_be_compared.get("end_time"))
            start_time2 = self.__parse_time(self.__event_to_compare.get("start_time"))
            end_time2 = self.__parse_time(self.__event_to_compare.get("end_time"))
            if start_time1 < end_time2 and end_time1 > start_time2:
                return True
        return False

    def __parse_time(self, time):
        return datetime.strptime(time, "%H:%M")

    def __check_field_equal(self, field: str) -> bool:
        return self.__event_to_be_compared.get(field) == self.__event_to_compare.get(
            field
        )
