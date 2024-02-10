from bson.objectid import ObjectId
from pymongo.collection import Collection
from pymongo.operations import UpdateOne

from src.common.database import database
from src.common.singleton_meta import SingletonMeta


class AllocationRepository(metaclass=SingletonMeta):
    __events_collection: Collection

    def __init__(self):
        self.__events_collection = database["events"]

    def update_many_allocations(self, events_specifications: list):
        formatted_events = self.__format_events_to_allocate(events_specifications)
        bulk_operations = [
            UpdateOne({"_id": event["_id"]}, {"$set": event})
            for event in formatted_events
        ]
        result = self.__events_collection.bulk_write(bulk_operations)

        return result.modified_count

    def __format_events_to_allocate(self, events_specifications):
        return [
            {
                "_id": ObjectId(event["id"]),
                "preferences.building_id": ObjectId(event["building_id"]),
                "classroom": event["classroom"],
                "has_to_be_allocated": False,
            }
            for event in events_specifications
        ]
