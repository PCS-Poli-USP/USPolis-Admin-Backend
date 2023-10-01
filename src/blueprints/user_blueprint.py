from flask import Blueprint, request
from datetime import datetime
from bson.json_util import dumps
from bson.objectid import ObjectId
from bson import json_util
from marshmallow import ValidationError
from pymongo.errors import DuplicateKeyError, PyMongoError
from flasgger import swag_from
from src.common.utils.prettify_id import prettify_id

from src.common.database import database
from src.schemas.user_schemas import UserSchema

user_blueprint = Blueprint("user", __name__, url_prefix="/api/user")
user_schema = UserSchema()
user_collection = database["user"]

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
        new_user = user_schema.load(request.json)
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
        updated_user = user_schema.load(request.json)
        updated_user["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        updated_user["updated_by"] = request.headers.get("username")

        result = user_collection.update_one({"_id": user_id}, {"$set": updated_user})

        return dumps(result.modified_count)

    except ValidationError as err:
        return {"message": err.messages}, 400

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500

@user_blueprint.delete("/<user_id>")
def delete_user(user_id):
    try:
        result = user_collection.delete_one({"_id": user_id})
        return dumps(result.deleted_count)

    except PyMongoError as err:
        return {"message": err.details["errmsg"]}, 400

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500