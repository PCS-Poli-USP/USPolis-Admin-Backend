from threading import Lock

from bson.objectid import ObjectId
from pymongo.collection import Collection
from pymongo.operations import UpdateOne

from src.common.database import database
from src.repository.building_repository import BuildingRepository


class SingletonMeta(type):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]

class AllocationRepository(metaclass=SingletonMeta):
    __events_collection: Collection

    def __init__(self):
        self.__events_collection = database["events"]
        self._building_repository = BuildingRepository()

    def update_many_allocations(
        self, events_ids: list, building_id: str, classroom: str
    ) -> int:
        building = self._building_repository.get_by_id(building_id)
        update_operations = [
            UpdateOne(
                {"_id": ObjectId(event_id)},
                {
                    "$set": {
                        "preferences.building_id": ObjectId(building_id),
                        "building": building["name"],
                        "classroom": classroom,
                        "has_to_be_allocated": False,
                    }
                },
            )
            for event_id in events_ids
        ]
        result = self.__events_collection.bulk_write(update_operations)
        return result.modified_count
