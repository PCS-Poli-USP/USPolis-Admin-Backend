from flask import Blueprint, request
from bson.json_util import dumps
from marshmallow import ValidationError
from pymongo.errors import DuplicateKeyError, PyMongoError
from flasgger import swag_from

from src.common.database import database
from src.schemas.subject_schema import SubjectSchema

subject_blueprint = Blueprint("subjects", __name__, url_prefix="/api/subjects")

subjects = database["subjects"]
subjects.create_index("subject_code", unique=True)

subject_schema = SubjectSchema()

yaml_files = "../swagger/subjects"

@subject_blueprint.route("", methods=["GET"])
@swag_from(f"{yaml_files}/get_all_subjects.yml")
def get_all_subjects():

  result = subjects.find({}, { "_id" : 0 })
  resultList = list(result)

  return dumps(resultList)


@subject_blueprint.route("", methods=["POST"])
@swag_from(f"{yaml_files}/create_subject.yml")
def create_subject():
  try:
    dict_request_body = request.json
    subject_schema.load(dict_request_body)

    result = subjects.insert_one(dict_request_body)

    return dumps(result.inserted_id)

  except DuplicateKeyError as err:
    return { "message" : err.details["errmsg"] }, 400

  except ValidationError as err:
    return { "message" : err.messages }, 400


@subject_blueprint.route("<code>", methods=["DELETE"])
def delete_subject(code):
  query = { "subject_code" : code }
  try:
    result = subjects.delete_one(query).deleted_count

    if not result: raise PyMongoError(f"{code} not found")

    return dumps(result)

  except PyMongoError as err:
    return { "message" : err._message }, 400