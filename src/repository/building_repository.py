from __future__ import annotations
from threading import Lock

import dotenv
from bson.objectid import ObjectId

from src.common.database import database

dotenv.load_dotenv()

class SingletonMeta(type):
    _instances = {}

    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class BuildingRepository(metaclass=SingletonMeta):
    def __init__(self):
        self._building_collection = database["building"]
        self._building_collection.create_index("name", unique=True)

    def list(self) -> list[dict]:
        buildings_cursor = self._building_collection.find()
        buildings = list(buildings_cursor)
        return buildings

    def get_by_id(self, building_id: str):
        self._building_collection = database["building"]
        building = self._building_collection.find_one({"_id": ObjectId(building_id)})
        return building
    
    def get_by_name(self, building_name: str):
        self._building_collection = database["building"]
        building = self._building_collection.find_one({"name": building_name})
        return building

    def check_ids_array(self, building_ids: list[str]):
        self._building_collection = database["building"]
        buildings = list(
            self._building_collection.find(
                {
                    "_id": {
                        "$in": [ObjectId(building_id) for building_id in building_ids]
                    }
                },
                {"_id": 1},
            )
        )
        buildings_ids_list = [building["_id"] for building in buildings]
        return buildings_ids_list

    def insert(self, building: dict):
        self._building_collection = database["building"]

        result = self._building_collection.insert_one(building)
        return {"id": str(result.inserted_id)}

    def update(self, building_id: str, building: dict):
        self._building_collection = database["building"]

        result = self._building_collection.update_one(
            {"_id": ObjectId(building_id)}, {"$set": building}
        )
        return result.modified_count

    def delete(self, building_id: str):
        self._building_collection = database["building"]

        result = self._building_collection.delete_one({"_id": ObjectId(building_id)})
        return result.deleted_count
