from datetime import datetime

from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import Blueprint, request
from marshmallow import ValidationError
from pymongo.errors import DuplicateKeyError, PyMongoError

import src.services.user.user_services as user_services
from src.common.database import database
from src.common.utils.prettify_id import prettify_id, recursive_prettify_id
from src.middlewares.auth_middleware import admin_middleware, auth_middleware
from src.repository.building_repository import BuildingRepository
from src.repository.user_repository import UserRepository
from src.schemas.user_schemas import UserInputSchema

user_blueprint = Blueprint("user", __name__, url_prefix="/api/user")
user_input_schema = UserInputSchema()
building_collection = database["building"]
user_repository = UserRepository()
building_repository = BuildingRepository()


@user_blueprint.before_request
def _():
    return admin_middleware()


@user_blueprint.get("")
def get_all_users():
    users = user_repository.list_with_buildings()
    recursive_prettify_id(users)
    return dumps(users)


@user_blueprint.get("/<user_id>")
def get_user(user_id):
    user = user_repository.get_by_id(user_id)
    prettify_id(user)
    return dumps(user)


@user_blueprint.post("")
def create_user():
    try:
        username = request.user.get("Username")

        new_user = user_input_schema.load(request.json)

        new_user["username"] = new_user["username"].lower()

        if " " in new_user.get("username"):
            return {"message": "Username cannot contain spaces"}, 400

        try:
            new_user["cognito_id"] = user_services.cognito_create_user(
                new_user["username"], new_user["email"]
            )
        except user_services.UserExistsException:
            return {"message": "Username already exists"}, 400

        building_ids = new_user.get("building_ids")
        if building_ids is not None:
            try:
                new_user["building_ids"] = building_repository.check_ids_array(
                    building_ids
                )
            except PyMongoError as err:
                print(err)
                return {
                    "message": f"Error checking building ids:\n{err.details['errmsg']}"
                }, 400

        new_user["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        new_user["created_by"] = username

        return user_repository.insert(new_user)
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
        logged_username = request.user.get("Username")
        logged_user = user_repository.get_by_username(logged_username)

        updated_user = user_input_schema.load(request.json)

        if user_id == str(logged_user.get("_id")) and (
            updated_user.get("isAdmin") is None or updated_user.get("isAdmin") is False
        ):
            return {"message": "Cannot change your own admin status"}, 400

        if updated_user.get("isAdmin") is True:
            updated_user["building_ids"] = []

        updated_user["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        updated_user["updated_by"] = logged_username
        building_ids = updated_user.get("building_ids")
        if building_ids is not None:
            try:
                updated_user["building_ids"] = building_repository.check_ids_array(
                    building_ids
                )
            except PyMongoError as err:
                print(err)
                return {
                    "message": f"Error checking building ids:\n{err.details['errmsg']}"
                }, 400

        result = user_repository.update(user_id, updated_user)

        return dumps(result)

    except ValidationError as err:
        return {"message": err.messages}, 400

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500


@user_blueprint.delete("/<user_id>")
def delete_user(user_id):
    try:
        logged_username = request.user.get("Username")
        user = user_repository.get_by_id(user_id)

        if logged_username == user.get("username"):
            return {"message": "Admins cannot delete themselves"}, 400

        user_services.cognito_delete_user(user.get("username"))
        result = user_repository.delete(user_id)
        return dumps(result)

    except PyMongoError as err:
        return {"message": err.details["errmsg"]}, 400

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500
