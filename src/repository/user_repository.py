from __future__ import annotations
import os
from pymongo import MongoClient
from src.common.singleton_meta import SingletonMeta
from bson.objectid import ObjectId
import dotenv

dotenv.load_dotenv()


class UserRepository(metaclass=SingletonMeta):
    __uri = os.environ.get("CONN_STR")
    __PORT: int = 27017

    def __init__(self):
        with MongoClient(self.__uri, self.__PORT) as client:
            user_collection = client["uspolis"]["user"]
            user_collection.create_index("username", unique=True)

    def list_with_buildings(self):
        with MongoClient(self.__uri, self.__PORT) as client:
            user_collection = client["uspolis"]["user"]
            users_cursor = user_collection.aggregate(
                [
                    {
                        "$lookup": {
                            "from": "building",  # name of building collection
                            "localField": "building_ids",  # name of field in user collection
                            "foreignField": "_id",  # name of field in building collection
                            "as": "buildings",  # name of new field in user collection
                        }
                    },
                    {
                        "$project": {
                            "cognito_id": 0,  # Exclude the "cognito_id" field
                            "building_ids": 0,  # Exclude the "building_ids" field
                        }
                    },
                ]
            )
            users = list(users_cursor)
            return users

    def get_by_id(self, user_id: str):
        '''Returns a user by its MONGO ID, not AWS ID!'''
        with MongoClient(self.__uri, self.__PORT) as client:
            user_collection = client["uspolis"]["user"]
            user = user_collection.find_one({"_id": ObjectId(user_id)})
            return user

    def get_by_username(self, username: str):
        with MongoClient(self.__uri, self.__PORT) as client:
            user_collection = client["uspolis"]["user"]
            user = user_collection.find_one({"username": username}, {"cognito_id": 0})
            return user

    def is_admin(self, username: str) -> bool:
        with MongoClient(self.__uri, self.__PORT) as client:
            user_collection = client["uspolis"]["user"]
            user = user_collection.find_one({"username": username})
            if user is None:
                return False
            isAdmin = user.get("isAdmin")
            if isAdmin is None:
                return False
            return isAdmin

    def insert(self, user: dict):
        with MongoClient(self.__uri, self.__PORT) as client:
            user_collection = client["uspolis"]["user"]

            result = user_collection.insert_one(user)
            return {"id": str(result.inserted_id)}

    def update(self, user_id: str, user: dict):
        with MongoClient(self.__uri, self.__PORT) as client:
            user_collection = client["uspolis"]["user"]

            result = user_collection.update_one(
                {"_id": ObjectId(user_id)}, {"$set": user}
            )
            return result.modified_count

    def delete(self, user_id: str):
        with MongoClient(self.__uri, self.__PORT) as client:
            user_collection = client["uspolis"]["user"]

            result = user_collection.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count
