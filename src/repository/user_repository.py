from __future__ import annotations

import dotenv
from bson.objectid import ObjectId

from src.common.database import database
from src.common.singleton_meta import SingletonMeta

dotenv.load_dotenv()


class UserNotFoundException(Exception):
    pass


class UserRepository(metaclass=SingletonMeta):
    def __init__(self):
        self._user_collection = database["user"]
        self._user_collection.create_index("username", unique=True)

    def list_with_buildings(self):
        users_cursor = self._user_collection.aggregate(
            [
                {
                    "$lookup": {
                        "from": "building",
                        "localField": "building_ids",
                        "foreignField": "_id",
                        "as": "buildings",
                    }
                },
                {
                    "$project": {
                        "cognito_id": 0,
                        "building_ids": 0,
                    }
                },
            ]
        )
        users = list(users_cursor)
        return users

    def get_by_id(self, user_id: str):
        """Returns a user by its MONGO ID, not AWS ID!"""
        user = self._user_collection.find_one({"_id": ObjectId(user_id)})
        return user

    def get_by_username(self, username: str):
        user_cursor = self._user_collection.aggregate(
            [
                {"$match": {"username": username}},
                {
                    "$lookup": {
                        "from": "building",
                        "localField": "building_ids",
                        "foreignField": "_id",
                        "as": "buildings",
                    }
                },
                {
                    "$project": {
                        "cognito_id": 0,
                        "building_ids": 0,
                    }
                },
            ]
        )
        user = next(user_cursor, None)  # Get the first user (or None if not found)
        if user is None:
            raise UserNotFoundException(f"User '{username}' not found")
        return user

    def is_admin(self, username: str) -> bool:
        user = self._user_collection.find_one({"username": username})
        if user is None:
            return False
        isAdmin = user.get("isAdmin")
        if isAdmin is None:
            return False
        return isAdmin

    def insert(self, user: dict):
        result = self._user_collection.insert_one(user)
        return {"id": str(result.inserted_id)}

    def update(self, user_id: str, user: dict):
        result = self._user_collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": user}
        )
        return result.modified_count

    def delete(self, user_id: str):
        result = self._user_collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count
