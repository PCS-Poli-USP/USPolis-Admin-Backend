from flask import Blueprint, request
from datetime import datetime
from bson.json_util import dumps
from bson.objectid import ObjectId
from marshmallow import ValidationError
from pymongo.errors import DuplicateKeyError, PyMongoError
from src.common.utils.prettify_id import prettify_id
from src.common.database import database
from src.schemas.user_schemas import UserInputSchema
from src.middlewares.auth_middleware import auth_middleware
from src.repository.user_repository import UserRepository
from src.repository.building_repository import BuildingRepository
import src.services.user.user_services as user_services

user_blueprint = Blueprint("user", __name__, url_prefix="/api/user")
user_input_schema = UserInputSchema()
user_collection = database["user"]
building_collection = database["building"]
user_collection.create_index("username", unique=True)
user_repository = UserRepository()
building_repository = BuildingRepository()


@user_blueprint.before_request
def _():
    return auth_middleware()


@user_blueprint.get("")
def get_all_users():
    users = user_repository.list()
    for user in users:
        prettify_id(user)
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
        username = request.user.get("Username")
        updated_user = user_input_schema.load(request.json)
        updated_user["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        updated_user["updated_by"] = username

        result = user_repository.update(user_id, updated_user)

        return dumps(result.modified_count)

    except ValidationError as err:
        return {"message": err.messages}, 400

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500


@user_blueprint.delete("/<user_id>")
def delete_user(user_id):
    try:
        result = user_repository.delete(user_id)
        return dumps(result.deleted_count)

    except PyMongoError as err:
        return {"message": err.details["errmsg"]}, 400

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500
