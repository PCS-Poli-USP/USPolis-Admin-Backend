from datetime import datetime

from bson.json_util import dumps
from flasgger import swag_from
from flask import Blueprint, request
from marshmallow import ValidationError
from pymongo.errors import DuplicateKeyError, PyMongoError

from src.common.database import database
from src.common.general_error import GeneralError
from src.common.utils.classroom.classroom_mapper import get_classroom_schedule
from src.common.utils.prettify_id import prettify_id, recursive_prettify_id
from src.common.utils.validate_body import validate_body
from src.common.verify_building_permission import verify_building_permission
from src.middlewares.auth_middleware import auth_middleware
from src.repository.building_repository import BuildingRepository
from src.repository.classrooms_repository import ClassroomsRepository
from src.repository.events_repository import EventsRepository
from src.repository.user_repository import UserRepository
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
user_repository = UserRepository()
building_repository = BuildingRepository()

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
    result = classrooms.find({"created_by": username})
    resultList = list(result)
    resultList = recursive_prettify_id(resultList)

    return dumps(resultList)


@classroom_blueprint.route("schedules")
def get_all_classrooms_schedules():
    try:
        username = request.user.get("Username")
        classroom_schedules = []
        classroom_list = list(classrooms.find({"created_by": username}, {"_id": 0}))
        for classroom in classroom_list:
            schedule = get_classroom_schedule(classroom)
            schedule["classroom"] = classroom["classroom_name"]
            schedule["capacity"] = classroom["capacity"]
            classroom_schedules.append(schedule)
        return {"schedules": classroom_schedules}

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500


@classroom_blueprint.route("", methods=["POST"])
@swag_from(f"{yaml_files}/create_classroom.yml")
def create_classroom():
    try:
        username = request.user.get("Username")
        logged_user = user_repository.get_by_username(username)
        if logged_user is None:
            return {"message": "User not found"}, 404

        logged_user_building_ids = [
            str(building["_id"]) for building in logged_user["buildings"]
        ]
        logged_user_is_admin = user_repository.is_admin(username)

        classroom_schema.load(request.json)
        payload = request.json

        building_name = payload["building"]
        building = building_repository.get_by_name(building_name)
        if building is None:
            return {"message": "Building not found"}, 404
        building_id = str(building["_id"])
        if building_id not in logged_user_building_ids and not logged_user_is_admin:
            return {"message": "You don't have permission to access this building"}, 403

        payload["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        payload["created_by"] = request.user.get("Username")

        result = classrooms.insert_one(payload)

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
            result = classrooms.find_one(query)
            result = recursive_prettify_id(result)

        if request.method == "DELETE":
            result = classrooms.delete_one(query).deleted_count

        if request.method == "PUT":
            classroom_schema.load(request.json)
            dict_request_body = request.json
            dict_request_body["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")

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
