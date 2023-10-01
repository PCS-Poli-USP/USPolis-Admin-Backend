from flask import Blueprint, request
from datetime import datetime
from bson.json_util import dumps
from bson.objectid import ObjectId
from marshmallow import ValidationError
from pymongo.errors import DuplicateKeyError, PyMongoError
from src.common.utils.prettify_id import prettify_id

from src.common.database import database
from src.schemas.user_schemas import UserInputSchema

user_blueprint = Blueprint("user", __name__, url_prefix="/api/user")
user_input_schema = UserInputSchema()
user_collection = database["user"]
building_collection = database["building"]
user_collection.create_index("username", unique=True)


@user_blueprint.get("")
def get_all_users():
    users_cursor = user_collection.find()
    users = list(users_cursor)
    for user in users:
        prettify_id(user)
    return dumps(users)


@user_blueprint.get("/<user_id>")
def get_user(user_id):
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    prettify_id(user)
    return dumps(user)


@user_blueprint.post("")
def create_user():
    try:
        username = request.headers.get("username")
        new_user = user_input_schema.load(request.json)
        new_user["buildings"] = []
        if new_user.get("building_names") is not None:
            for building_name in new_user["building_names"]:
                building = building_collection.find_one({"name": building_name})
                if building is None:
                    return {"message": "Building not found"}, 404
                new_user["buildings"].append(building)
        new_user.pop("building_names", None)
        new_user["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        new_user["created_by"] = username

        result = user_collection.insert_one(new_user)
        return dumps(result.inserted_id)

    except DuplicateKeyError as err:
        return {"message": err.details["errmsg"]}, 400

    except ValidationError as err:
        return {"message": err.messages}, 400

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500


@user_blueprint.put("/<user_id>")
def update_user(user_id):
    try:
        username = request.headers.get("username")
        updated_user = user_input_schema.load(request.json)
        updated_user["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        updated_user["updated_by"] = request.headers.get("username")

        result = user_collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": updated_user}
        )

        return dumps(result.modified_count)

    except ValidationError as err:
        return {"message": err.messages}, 400

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500


@user_blueprint.delete("/<user_id>")
def delete_user(user_id):
    try:
        result = user_collection.delete_one({"_id": ObjectId(user_id)})
        return dumps(result.deleted_count)

    except PyMongoError as err:
        return {"message": err.details["errmsg"]}, 400

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500
