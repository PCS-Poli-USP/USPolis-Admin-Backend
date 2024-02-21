from datetime import datetime

from bson.json_util import dumps
from flask import Blueprint, request
from marshmallow import ValidationError
from pymongo.errors import DuplicateKeyError, PyMongoError

from src.common.database import database
from src.common.utils.prettify_id import prettify_id
from src.middlewares.auth_middleware import auth_middleware
from src.repository.building_repository import BuildingRepository
from src.schemas.building_schemas import BuildingInputSchema

building_blueprint = Blueprint("building", __name__, url_prefix="/api/building")
building_input_schema = BuildingInputSchema()
building_repository = BuildingRepository()


@building_blueprint.before_request
def _():
    return auth_middleware()


@building_blueprint.get("")
def get_all_buildings():
    buildings = building_repository.list()
    for building in buildings:
        prettify_id(building)
    return dumps(buildings)


@building_blueprint.get("/<building_id>")
def get_building(building_id):
    building = building_repository.get_by_id(building_id)
    if building is None:
        return {"message": f"Building {building_id} not found found"}, 404
    return dumps(prettify_id(building))


@building_blueprint.post("")
def create_building():
    try:
        username = request.user.get("Username")
        new_building = building_input_schema.load(request.json)
        new_building["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        new_building["created_by"] = username

        return building_repository.insert(new_building)

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
        updated_building = building_input_schema.load(request.json)
        updated_building["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        updated_building["updated_by"] = request.user.get("Username")

        result = building_repository.update(building_id, updated_building)
        return dumps(result)

    except ValidationError as err:
        return {"message": err.messages}, 400

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500


@building_blueprint.delete("/<building_id>")
def delete_building(building_id):
    try:
        result = building_repository.delete(building_id)
        return dumps(result)

    except PyMongoError as err:
        return {"message": err.details["errmsg"]}, 400

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500
