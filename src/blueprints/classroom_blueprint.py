from flask import Blueprint, request
from bson.json_util import dumps
from marshmallow import ValidationError
from pymongo.errors import DuplicateKeyError, PyMongoError
from datetime import datetime
from flasgger import swag_from

from src.common.database import database
from src.schemas.classroom_schema import ClassroomSchema, AvailableClassroomsQuerySchema

classroom_blueprint = Blueprint("classrooms", __name__, url_prefix="/api/classrooms")

classrooms = database["classrooms"]
events = database["events"]

# classroom_name not unique
# classrooms.create_index({ "classroom_name" : 1, "building" : 1 }, unique=True)

classroom_schema = ClassroomSchema()
available_classrooms_query_schema = AvailableClassroomsQuerySchema()

yaml_files = "../swagger/classrooms"

@classroom_blueprint.route("")
@swag_from(f"{yaml_files}/get_all_classrooms.yml")
def get_all_classrooms():
  username = request.headers.get('username')
  result = classrooms.find({"created_by" : username}, { "_id" : 0 })
  resultList = list(result)

  return dumps(resultList)


@classroom_blueprint.route("", methods=["POST"])
@swag_from(f"{yaml_files}/create_classroom.yml")
def create_classroom():
  try:
    classroom_schema.load(request.json)
    dict_request_body = request.json

    dict_request_body['updated_at'] = datetime.now().strftime("%d/%m/%Y %H:%M")
    dict_request_body['created_by'] = request.headers.get('username')

    result = classrooms.insert_one(dict_request_body)

    return dumps(result.inserted_id)

  except DuplicateKeyError as err:
    return { "message" : err.details["errmsg"] }, 400

  except ValidationError as err:
    return { "message" : err.messages }, 400

  except Exception as ex:
    print(ex)
    return { "message" : str(ex) }, 500


@classroom_blueprint.route("/<name>", methods=["GET", "DELETE", "PUT"])
@swag_from(f"{yaml_files}/classroom_by_name.yml")
def classroom_by_name(name):
  try:
    username = request.headers.get('username')
    query = { "classroom_name" : name, "created_by" : username }
    if request.method == "GET":
      result = classrooms.find_one(query, { "_id" : 0 })

    if request.method == "DELETE":
      result = classrooms.delete_one(query).deleted_count

    if request.method == "PUT":
      classroom_schema.load(request.json)
      dict_request_body = request.json
      dict_request_body['updated_at'] = datetime.now().strftime("%d/%m/%Y %H:%M")
      dict_request_body['created_by'] = request.headers.get('username')

      update_set = {"$set" : dict_request_body }
      result = classrooms.update_one(query, update_set).modified_count

    if not result: raise PyMongoError(f"{name} not found")

    return dumps(result)

  except ValidationError as err:
    return { "message" : err.messages }, 400

  except PyMongoError as err:
    return { "message" : err._message }, 400

  except Exception as ex:
    print(ex)
    return { "message" : str(ex) }, 500

@classroom_blueprint.route("/available")
@swag_from(f"{yaml_files}/get_available_classrooms.yml")
def get_available_classrooms():
  try:
    params = available_classrooms_query_schema.load(request.args)
    unavailable_classrooms = events.find(
      {
        "week_day" : params["week_day"],
        "start_time": { "$lte" : params["end_time"] },
        "end_time" : { "$gte" : params["start_time"] }
      },
      { "classroom" : True , "_id" : False }
      ).distinct("classroom")

    username = request.headers.get('username')
    classrooms_list = list(classrooms.find(
      { "created_by" : username }, { "classroom_name" : True, "capacity" : True, "building" : True, "_id" : False }
      ))

    available_classrooms = [c for c in classrooms_list if c["classroom_name"] not in unavailable_classrooms]

    return dumps(available_classrooms)

  except ValidationError as err:
    return { "message" : err.messages }, 400

  except Exception as ex:
    print(ex)
    return { "message" : str(ex) }, 500
