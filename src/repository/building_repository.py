from __future__ import annotations
import os
from pymongo import MongoClient
from src.common.singleton_meta import SingletonMeta
from bson.objectid import ObjectId


class BuildingRepository(metaclass=SingletonMeta):
    __uri = os.environ.get("CONN_STR")
    __PORT: int = 27017

    def __init__(self):
        with MongoClient(self.__uri, self.__PORT) as client:
            building_collection = client["uspolis"]["building"]
            building_collection.create_index("name", unique=True)

    def list(self) -> list[dict]:
        with MongoClient(self.__uri, self.__PORT) as client:
            database = client["uspolis"]
            building_collection = database["building"]
            buildings_cursor = building_collection.find()
            buildings = list(buildings_cursor)
            return buildings

    def get_by_id(self, building_id: str):
        with MongoClient(self.__uri, self.__PORT) as client:
            database = client["uspolis"]
            building_collection = database["building"]
            building = building_collection.find_one({"_id": ObjectId(building_id)})
            return building

    def check_ids_array(self, building_ids: list[str]):
        with MongoClient(self.__uri, self.__PORT) as client:
            database = client["uspolis"]
            building_collection = database["building"]
            buildings = list(
                building_collection.find(
                    {
                        "_id": {
                            "$in": [
                                ObjectId(building_id) for building_id in building_ids
                            ]
                        }
                    },
                    {"_id": 1},
                )
            )
            buildings_ids_list = [building["_id"] for building in buildings]
            return buildings_ids_list

    def insert(self, building: dict):
        with MongoClient(self.__uri, self.__PORT) as client:
            database = client["uspolis"]
            building_collection = database["building"]

            result = building_collection.insert_one(building)
            return {"id": str(result.inserted_id)}

    def update(self, building_id: str, building: dict):
        with MongoClient(self.__uri, self.__PORT) as client:
            database = client["uspolis"]
            building_collection = database["building"]

            result = building_collection.update_one(
                {"_id": ObjectId(building_id)}, {"$set": building}
            )
            return result.modified_count

    def delete(self, building_id: str):
        with MongoClient(self.__uri, self.__PORT) as client:
            database = client["uspolis"]
            building_collection = database["building"]

            result = building_collection.delete_one({"_id": ObjectId(building_id)})
            return result.deleted_count
