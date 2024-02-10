from bson.objectid import ObjectId
from pymongo.collection import Collection
from pymongo.operations import UpdateOne

from src.common.database import database
from src.common.singleton_meta import SingletonMeta


class AllocationRepository(metaclass=SingletonMeta):
    __events_collection: Collection

    def __init__(self):
        self.__events_collection = database["events"]

    def update_many_allocations(
        self, events_ids: list, building_id: str, classroom: str
    ) -> int:
        update_operations = [
            UpdateOne(
                {"_id": ObjectId(event_id)},
                {
                    "$set": {
                        "preferences.building_id": ObjectId(building_id),
                        "classroom": classroom,
                        "has_to_be_allocated": False,
                    }
                },
            )
            for event_id in events_ids
        ]
        result = self.__events_collection.bulk_write(update_operations)
        return result.modified_count
