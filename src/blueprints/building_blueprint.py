from flask import Blueprint, request
from datetime import datetime
from bson.json_util import dumps
from bson.objectid import ObjectId
from marshmallow import ValidationError
from pymongo.errors import DuplicateKeyError, PyMongoError
from src.common.utils.prettify_id import prettify_id
from src.middlewares.auth_middleware import auth_middleware

from src.common.database import database
from src.schemas.building_schemas import BuildingInputSchema

building_blueprint = Blueprint("building", __name__, url_prefix="/api/building")
building_input_schema = BuildingInputSchema()
building_collection = database["building"]
building_collection.create_index("name", unique=True)


@building_blueprint.before_request
def _():
    return auth_middleware()


@building_blueprint.get("")
def get_all_buildings():
    buildings_cursor = building_collection.find()
    buildings = list(buildings_cursor)
    for building in buildings:
        prettify_id(building)
    return dumps(buildings)


@building_blueprint.get("/<building_id>")
def get_building(building_id):
    building = building_collection.find_one({"_id": ObjectId(building_id)})
    prettify_id(building)
    return dumps(building)


@building_blueprint.post("")
def create_building():
    try:
        username = request.headers.get("username")
        new_building = building_input_schema.load(request.json)
        new_building["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        new_building["created_by"] = username

        result = building_collection.insert_one(new_building)
        return dumps(result.inserted_id)

    except DuplicateKeyError as err:
        return {"message": err.details["errmsg"]}, 400

    except ValidationError as err:
        return {"message": err.messages}, 400

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500


@building_blueprint.put("/<building_id>")
def update_building(building_id):
    try:
        username = request.headers.get("username")
        updated_building = building_input_schema.load(request.json)
        updated_building["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        updated_building["updated_by"] = request.headers.get("username")

        result = building_collection.update_one(
            {"_id": ObjectId(building_id)}, {"$set": updated_building}
        )
        return dumps(result.modified_count)

    except ValidationError as err:
        return {"message": err.messages}, 400

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500


@building_blueprint.delete("/<building_id>")
def delete_building(building_id):
    try:
        result = building_collection.delete_one({"_id": ObjectId(building_id)})
        return dumps(result.deleted_count)

    except PyMongoError as err:
        return {"message": err.details["errmsg"]}, 400

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500
