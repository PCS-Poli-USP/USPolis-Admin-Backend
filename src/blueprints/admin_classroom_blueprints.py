from datetime import datetime

from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import request

from src.blueprints.blueprint_builder import build_admin_blueprint
from src.common.database import database
from src.schemas.classroom_schema import ClassroomSchema

admin_classroom_blueprint = build_admin_blueprint(
    "admin_classrooms", "/api/admin-classrooms"
)

classrooms_collection = database["classrooms"]


@admin_classroom_blueprint.put("<id>")
def update_classroom(id):
    classroom_schema = ClassroomSchema()
    classroom_schema.load(request.json)
    dict_request_body = request.json
    dict_request_body["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")

    update_set = {"$set": dict_request_body}
    result = classrooms_collection.update_one(
        {"_id": ObjectId(id)}, update_set
    ).modified_count

    return dumps(result)
