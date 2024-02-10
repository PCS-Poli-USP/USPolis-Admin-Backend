from datetime import datetime

from bson.json_util import dumps
from flasgger import swag_from
from flask import Blueprint, request
from marshmallow import ValidationError
from pymongo.errors import DuplicateKeyError, PyMongoError

from src.common.database import database
from src.common.general_error import GeneralError
from src.common.utils.validate_body import validate_body
from src.common.verify_building_permission import verify_building_permission
from src.middlewares.auth_middleware import auth_middleware
from src.repository.classrooms_repository import ClassroomsRepository
from src.repository.events_repository import EventsRepository
from src.schemas.classroom_schema import (
    AvailableClassroomsQuerySchema,
    ClassroomSchema,
    GetAvailableClassroomsSchema,
)
from src.services.classrooms.list_available_classrooms import list_available_classrooms
from src.services.conflicts.conflict_calculator import ConflictCalculator

classroom_blueprint = Blueprint("classrooms", __name__, url_prefix="/api/classrooms")

classrooms = database["classrooms"]
events = database["events"]
classrooms_repository = ClassroomsRepository()
events_repository = EventsRepository()

# classroom_name not unique
# classrooms.create_index({ "classroom_name" : 1, "building" : 1 }, unique=True)

classroom_schema = ClassroomSchema()
available_classrooms_query_schema = AvailableClassroomsQuerySchema()

yaml_files = "../swagger/classrooms"


@classroom_blueprint.before_request
def _():
    return auth_middleware()


@classroom_blueprint.route("")
@swag_from(f"{yaml_files}/get_all_classrooms.yml")
def get_all_classrooms():
    username = request.user.get("Username")
    result = classrooms.find({"created_by": username}, {"_id": 0})
    resultList = list(result)

    return dumps(resultList)


@classroom_blueprint.route("", methods=["POST"])
@swag_from(f"{yaml_files}/create_classroom.yml")
def create_classroom():
    try:
        classroom_schema.load(request.json)
        dict_request_body = request.json

        dict_request_body["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        dict_request_body["created_by"] = request.user.get("Username")

        result = classrooms.insert_one(dict_request_body)

        return dumps(result.inserted_id)

    except DuplicateKeyError as err:
        return {"message": err.details["errmsg"]}, 400

    except ValidationError as err:
        return {"message": err.messages}, 400

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500


@classroom_blueprint.route("/<name>", methods=["GET", "DELETE", "PUT"])
@swag_from(f"{yaml_files}/classroom_by_name.yml")
def classroom_by_name(name):
    try:
        username = request.user.get("Username")
        query = {"classroom_name": name, "created_by": username}
        if request.method == "GET":
            result = classrooms.find_one(query, {"_id": 0})

        if request.method == "DELETE":
            result = classrooms.delete_one(query).deleted_count

        if request.method == "PUT":
            classroom_schema.load(request.json)
            dict_request_body = request.json
            dict_request_body["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            dict_request_body["created_by"] = username

            update_set = {"$set": dict_request_body}
            result = classrooms.update_one(query, update_set).modified_count

        if not result:
            raise PyMongoError(f"{name} not found")

        return dumps(result)

    except ValidationError as err:
        return {"message": err.messages}, 400

    except PyMongoError as err:
        return {"message": err._message}, 400

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500


@classroom_blueprint.post("/available-with-conflict-check")
def get_available_classrooms_with_conflict_check():
    username = request.user.get("Username")
    schema = GetAvailableClassroomsSchema()
    body = request.json
    try:
        data = validate_body(body, schema)
        building_id = data.get("building_id")
        events_ids = data.get("events_ids")
        building_name = verify_building_permission(username, building_id)

        classrooms_list = list_available_classrooms(
            events_ids, building_id, building_name
        )

        return dumps(classrooms_list)

    except GeneralError as e:
        return e.get_tuple()
    except Exception as ex:
        return {"message": str(ex)}, 500


@classroom_blueprint.route("/available")
@swag_from(f"{yaml_files}/get_available_classrooms.yml")
def get_available_classrooms():
    try:
        username = request.user.get("Username")

        classrooms_list = list(
            classrooms.find(
                {"created_by": username},
                {
                    "classroom_name": True,
                    "capacity": True,
                    "building": True,
                    "_id": False,
                },
            )
        )

        available_classrooms = [c for c in classrooms_list]

        return dumps(available_classrooms)

    except ValidationError as err:
        return {"message": err.messages}, 400

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500
