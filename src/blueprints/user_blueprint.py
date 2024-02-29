from flask import Blueprint, request
from bson.json_util import dumps
from marshmallow import ValidationError
from pymongo.errors import DuplicateKeyError, PyMongoError
from flasgger import swag_from

from src.common.database import database
from src.schemas.user_schema import UserSchema

subject_blueprint = Blueprint("users", __name__, url_prefix="/api/users")

users = database["users"]
users.create_index("subject_code", unique=True)

user_schema = UserSchema()

# yaml_files = "../swagger/users"

@subject_blueprint.route("", methods=["GET"])
@swag_from(f"{yaml_files}/get_all_users.yaml")
def get_all_subjects():

  result = subjects.find({}, { "_id" : 0 })
  resultList = list(result)

  return dumps(resultList)
