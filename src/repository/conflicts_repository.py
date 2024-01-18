from src.common.database import database
from src.common.singleton_meta import SingletonMeta
from src.services.conflicts.conflict_calculator import ConflictCalculator


class ConflictRepository(metaclass=SingletonMeta):
    # public members
    def get_all(self):
        all_events = self.__get_all_events_list()
        conflictCalculator = ConflictCalculator(all_events)
        conflicts = conflictCalculator.calculate_conflicts_list()
        return conflicts

    # private members
    __events_tb = database["events"]

    def __get_all_events_list(self) -> list[dict]:
        return list(self.__events_tb.find())
