from flask import Blueprint, request
from bson.json_util import dumps
from marshmallow import EXCLUDE
from pymongo.errors import PyMongoError, DuplicateKeyError
from marshmallow import ValidationError
from datetime import datetime
from flasgger import swag_from
from bson.objectid import ObjectId

from src.common.database import database
from src.common.crawler import get_jupiter_class_infos
from src.schemas.class_schema import (
    ClassSchema,
    PreferencesSchema,
    HasToBeAllocatedClassesSchema,
)
from src.schemas.event_schema import EventSchema
from src.common.mappers.classes_mapper import break_class_into_events
from src.middlewares.auth_middleware import auth_middleware

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
                    "subscribers": {"$first": "$subscribers"},
                    "classrooms": {"$push": "$classroom"},
                }
            },
        ]
    )
    resultList = list(result)

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

        return dumps({"inserted" : inserted })
    
    except DuplicateKeyError as err:
        print(err)
        return {"message": err.details["errmsg"]}, 400

    except ValidationError as err:
        print(err)
        return {"message": err.messages}, 400

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500


@class_blueprint.route("many", methods=["POST"])
@swag_from(f"{yaml_files}/create_many_classes.yml")
def create_many_classes():
    try:
        subject_codes_list = request.json
        updated = []
        inserted = []
        username = request.user.get("Username")

        for subject_code in subject_codes_list:
            user = users.find_one({"username": username})
            preference_building = user["building"]
            subject_classes = get_jupiter_class_infos(subject_code)

            for class_info in subject_classes:
                class_schema_load = class_schema.load(class_info)
                events_list = break_class_into_events(
                    class_schema_load, preference_building
                )

                for event in events_list:
                    event_schema_load = event_schema.load(event)
                    event_schema_load["updated_at"] = datetime.now().strftime(
                        "%d/%m/%Y %H:%M"
                    )
                    event_schema_load["created_by"] = username

                    query = {
                        "class_code": event_schema_load["class_code"],
                        "subject_code": event_schema_load["subject_code"],
                        "week_day": event_schema_load["week_day"],
                        "created_by": event_schema_load["created_by"],
                    }
                    result = events.update_one(
                        query, {"$set": event_schema_load}, upsert=True
                    )
                    updated.append(
                        event_schema_load["subject_code"]
                    ) if result.matched_count else inserted.append(
                        event_schema_load["subject_code"]
                    )

        return dumps({"updated": updated, "inserted": inserted})

    except Exception as ex:
        print(ex)
        return {
            "message": f"Erro ao buscar informações das turmas - {subject_code}",
            "updated": updated,
            "inserted": inserted,
            "error": str(ex),
        }, 400


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
        has_to_be_allocated = request.json["has_to_be_allocated"]

        result = events.update_many(
            query,
            {
                "$set": {
                    "preferences": preferences_schema_load,
                    "has_to_be_allocated": has_to_be_allocated,
                }
            },
        )

        return dumps(result.modified_count)

    except PyMongoError as err:
        return {"message": err._message}


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
        updated = 0
        username = request.user.get("Username")

        for event in class_events:
            query = {
                "subject_code": subject_code,
                "class_code": class_code,
                "week_day": event["week_day_id"],
                "start_time": event["start_time_id"],
                "created_by": username,
            }

            result = events.update_one(
                query,
                {
                    "$set": {
                        "week_day": event["week_day"],
                        "start_time": event["start_time"],
                        "end_time": event["end_time"],
                        "professors": event["professors"],
                        "subscribers": event["subscribers"],
                        "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    }
                },
            )
            updated += result.matched_count

        return dumps({"updated": updated})

    except Exception as ex:
        print(ex)
        print("Eita")
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
