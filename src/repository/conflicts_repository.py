from threading import Lock
from src.common.database import database
from src.services.conflicts.conflict_calculator import ConflictCalculator


class SingletonMeta(type):
    _instances = {}

    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]

class ConflictRepository(metaclass=SingletonMeta):
    # public members
    def get_all(self):
        all_events = self.__get_all_events_list()
        conflicts = ConflictCalculator.calculate_conflicts_list(all_events)
        return conflicts

    # private members
    __events_tb = database["events"]

    def __get_all_events_list(self) -> list[dict]:
        return list(self.__events_tb.find({"has_to_be_allocated": False}))
