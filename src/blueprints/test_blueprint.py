from bson.json_util import dumps
from flasgger import swag_from
from flask import Blueprint, request

from src.common.database import database

test_blueprint = Blueprint("test", __name__, url_prefix="/api/test")

test_collection = database["test"]

@test_blueprint.route("")
def get_all_classrooms():
    # upsert a default value and get it
    test_collection.update_one({"_id": "test"}, {"$set": {"test": "test"}}, upsert=True)
    result = test_collection.find_one({"_id": "test"}, {"_id": 0})
    return dumps(result)
