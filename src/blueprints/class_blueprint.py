from datetime import datetime

from bson.json_util import dumps
from bson.objectid import ObjectId
from flasgger import swag_from
from flask import Blueprint, request
from marshmallow import EXCLUDE, ValidationError
from pymongo.errors import DuplicateKeyError, PyMongoError

from src.common.database import database
from src.common.utils.prettify_preferences import prettify_preferences
from src.middlewares.auth_middleware import auth_middleware
from src.repository.user_repository import UserRepository
from src.schemas.class_schema import (
    ClassSchema,
    HasToBeAllocatedClassesSchema,
    PreferencesSchema,
)
from src.schemas.event_schema import EventSchema

class_blueprint = Blueprint("classes", __name__, url_prefix="/api/classes")

# classes = database["classes"]
events = database["events"]
users = database["users"]

# USING UPSERT
# classes.create_index({ "class_code" : 1, "subject_code" : 1 }, unique=True)

class_schema = ClassSchema(unknown=EXCLUDE)
preferences_schema = PreferencesSchema(unknown=EXCLUDE)
has_to_be_allocated_schema = HasToBeAllocatedClassesSchema(many=True, unknown=EXCLUDE)
event_schema = EventSchema()
user_repository = UserRepository()

yaml_files = "../swagger/classes"


@class_blueprint.before_request
def _():
    return auth_middleware()


@class_blueprint.route("", methods=["GET"])
@swag_from(f"{yaml_files}/get_all_classes.yml")
def get_all_classes():
    username = request.user.get("Username")
    result = events.aggregate(
        [
            {"$match": {"created_by": username}},
            {
                "$group": {
                    "_id": {
                        "class_code": "$class_code",
                        "subject_code": "$subject_code",
                    },
                    "class_code": {"$first": "$class_code"},
                    "subject_code": {"$first": "$subject_code"},
                    "subject_name": {"$first": "$subject_name"},
                    "professors": {"$first": "$professors"},
                    "start_period": {"$first": "$start_period"},
                    "end_period": {"$first": "$end_period"},
                    "start_time": {"$push": "$start_time"},
                    "end_time": {"$push": "$end_time"},
                    "week_days": {"$push": "$week_day"},
                    "preferences": {"$first": "$preferences"},
                    "has_to_be_allocated": {"$first": "$has_to_be_allocated"},
                    "ignore_to_allocate": {"$first": "$ignore_to_allocate"},
                    "subscribers": {"$first": "$subscribers"},
                    "vacancies": {"$first": "$vacancies"},
                    "pendings": {"$first": "$pendings"},
                    "classrooms": {"$push": {"$ifNull": ["$classroom", "Não alocado"]}},
                    "buildings" : {"$push" : {"$ifNull": ["$building", "Não alocado"]}},

                    "events_ids": {"$push": {"$toString": "$_id"}},
                }
            },
        ]
    )
    resultList = list(result)
    for classes in resultList:
        prettify_preferences(classes["preferences"])
    return dumps(resultList)


@class_blueprint.route("", methods=["POST"])
def create_class():
    try:
        inserted = []
        username = request.user.get("Username")
        events_list = request.json
        for event in events_list:
            new_event = event_schema.load(event)
            building_id = new_event["preferences"]["building_id"]
            new_event["preferences"]["building_id"] = ObjectId(building_id)
            new_event["created_by"] = username
            new_event["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")

            result = events.insert_one(new_event)
            inserted.append(result.inserted_id)

        return dumps({"inserted": inserted})

    except DuplicateKeyError as err:
        print(err)
        return {"message": err.details["errmsg"]}, 400

    except ValidationError as err:
        print(err)
        return {"message": err.messages}, 400

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500


@class_blueprint.route("/<subject_code>/<class_code>", methods=["DELETE"])
@swag_from(f"{yaml_files}/delete_by_subject_class_code.yml")
def delete_by_subject_class_code(subject_code, class_code):
    username = request.user.get("Username")
    query = {
        "subject_code": subject_code,
        "class_code": class_code,
        "created_by": username,
    }

    try:
        result = events.delete_many(query).deleted_count
        if not result:
            raise PyMongoError(f"{subject_code} - {class_code} not found")
        return dumps(result)

    except PyMongoError as err:
        return {"message": err._message}


@class_blueprint.route("/preferences/<subject_code>/<class_code>", methods=["PATCH"])
@swag_from(f"{yaml_files}/update_preferences.yml")
def update_preferences(subject_code, class_code):
    username = request.user.get("Username")
    query = {
        "subject_code": subject_code,
        "class_code": class_code,
        "created_by": username,
    }

    try:
        preferences_schema_load = preferences_schema.load(request.json)
        building_id = preferences_schema_load["building_id"]
        preferences_schema_load["building_id"] = ObjectId(building_id)
        ignore_to_allocate = request.json["ignore_to_allocate"]

        result = events.update_many(
            query,
            {
                "$set": {
                    "preferences": preferences_schema_load,
                    "ignore_to_allocate": ignore_to_allocate,
                    "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
                }
            },
        )

        return dumps(result.modified_count)

    except PyMongoError as err:
        return {"message": err._message}
    except Exception as ex:
        print(str(ex))
        return {"message": "Erro ao atualizar prefrerencias", "error": str(ex)}, 500


@class_blueprint.route("/<subject_code>/<class_code>", methods=["GET"])
@swag_from(f"{yaml_files}/get_preferences.yml")
def get_preferences(subject_code, class_code):
    username = request.user.get("Username")
    query = {
        "subject_code": subject_code,
        "class_code": class_code,
        "created_by": username,
    }

    try:
        result = events.find_one(query, {"_id": 0})

        if not result:
            raise PyMongoError(f"{subject_code}/{class_code} not found")

        return dumps(result)

    except PyMongoError as err:
        return {"message": err._message}

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500


@class_blueprint.route("/<subject_code>/<class_code>", methods=["PATCH"])
@swag_from(f"{yaml_files}/edit_class.yml")
def edit_class(subject_code, class_code):
    try:
        class_events = request.json
        deleted = 0
        inserted = 0
        username = request.user.get("Username")

        query = {
            "subject_code": subject_code,
            "class_code": class_code,
            "created_by": username,
        }

        result = events.delete_many(query)
        deleted += result.deleted_count

        for event in class_events:
            event = event_schema.load(event)
            building_id = event["preferences"]["building_id"]
            event["preferences"]["building_id"] = ObjectId(building_id)
            event["created_by"] = username
            event["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")

            result = events.insert_one(event)
            inserted += 1

        return dumps({"inserted": inserted, "removed": deleted})

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500


@class_blueprint.route("has-to-be-allocated", methods=["PATCH"])
@swag_from(f"{yaml_files}/update_has_to_be_allocated.yml")
def update_has_to_be_allocated():
    try:
        username = request.user.get("Username")
        has_to_be_allocated_schema_load = has_to_be_allocated_schema.load(request.json)
        updated = 0

        for cls in has_to_be_allocated_schema_load:
            query = {
                "subject_code": cls["subject_code"],
                "class_code": cls["class_code"],
                "created_by": username,
            }
            result = events.update_many(
                query, {"$set": {"has_to_be_allocated": cls["has_to_be_allocated"]}}
            )

            updated += result.matched_count

        return dumps({"updated": updated})

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500
