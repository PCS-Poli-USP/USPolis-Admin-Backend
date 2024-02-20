from threading import Lock
from bson.objectid import ObjectId

from src.common.database import database


class SingletonMeta(type):
    _instances = {}

    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class EventsRepository(metaclass=SingletonMeta):
    def __init__(self):
        self.__events_tb = database["events"]

    def list_by_ids(self, ids: list[str]) -> list[dict]:
        query = {"_id": {"$in": [ObjectId(id) for id in ids]}}
        return list(self.__events_tb.find(query))

    def list_by_building_grouped_by_classroom(
        self, building_id
    ) -> dict[str, list[dict]]:
        query = {"preferences.building_id": ObjectId(building_id)}
        events = list(self.__events_tb.find(query))

        grouped_events = {}
        for event in events:
            classroom = event.get("classroom")
            if classroom is None:
                continue
            if classroom not in grouped_events:
                grouped_events[classroom] = []
            grouped_events[classroom].append(event)

        return grouped_events
