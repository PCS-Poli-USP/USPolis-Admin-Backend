from flask import Blueprint, request
from bson.json_util import dumps
from marshmallow import EXCLUDE, ValidationError
from pymongo.errors import PyMongoError
from datetime import datetime, timedelta
from flasgger import swag_from
from threading import Thread

from src.common.tasks import update_events_activeness
from src.common.database import database
from src.schemas.allocation_schema import AllocatorInputSchema, AllocatorOutputSchema
from src.common.allocation.new_allocator import allocate_classrooms
# from src.common.utils.event.events_formatter import clear_event_allocation
from src.middlewares.auth_middleware import auth_middleware

event_blueprint = Blueprint("events", __name__, url_prefix="/api/events")

events = database["events"]
classrooms = database["classrooms"]
allocations = database["allocations"]

# class id - class_code, subject_code
# event id - start_time, end_time, week_day
# classroom id - building, classroom

allocation_output_schema = AllocatorOutputSchema()
allocation_input_schema = AllocatorInputSchema(many=True, unknown=EXCLUDE)

yaml_files = "../swagger/events"


@event_blueprint.before_request
def _():
    return auth_middleware()


@event_blueprint.route("")
@swag_from(f"{yaml_files}/get_events.yml")
def get_events():
    username = request.user.get("Username")
    result = events.find({"created_by": username}, {"_id": 0})
    resultList = list(result)

    return dumps(resultList)


@event_blueprint.route("/<subject_code>/<class_code>", methods=["GET"])
def get_events_by_class(subject_code, class_code):
    username = request.user.get("Username")
    result = events.find(
        {"created_by": username, "subject_code": subject_code, "class_code": class_code})
    resultList = list(result)
    return dumps(resultList)


@event_blueprint.route("allocate", methods=["PATCH"])
@swag_from(f"{yaml_files}/save_new_allocation.yml")
def save_new_allocation():
    try:
        username = request.user.get("Username")
        result = events.update_many(
            {"created_by": username},
            {
                "$unset": {
                    "building": "",
                    "classroom": "",
                },
                "$set": {"has_to_be_allocated": True}
            },
        )
        classroom_list = list(classrooms.find(
            {"created_by": username, "ignore_to_allocate": False}, {"_id": 0}))
        event_list = list(events.find({"created_by": username}))
        result = allocate_classrooms(classroom_list, event_list)
        allocated_events = result[0]
        unallocated_events = result[1]

        filter = {"created_by": username}
        query = {
            "$set": {
                "allocated_events": allocated_events,
                "unallocated_events": unallocated_events,
                "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
            }
        }
        allocations.update_one(filter, query, upsert=True)

        return {"allocated": allocated_events, "unallocated": unallocated_events}

    except ValidationError as err:
        return {"message": err.messages}, 400

    except Exception as ex:
        return {"message": "Erro ao calcular alocação", "error": str(ex)}, 500


@event_blueprint.route("load", methods=["GET"])
def load_allocations():
    try:
        username = request.user.get("Username")
        result = allocations.find_one({"created_by": username})
        allocated_events = result["allocated_events"]
        unallocated_events = result["unallocated_events"]
        now = datetime.now().strftime("%d/%m/%Y %H:%M")

        for event in allocated_events:
            filter = {
                "subject_code": event["subject_code"],
                "class_code": event["class_code"],
                "week_day": event["week_day"],
                "start_time": event["start_time"],
                "created_by": username,
            }

            query = {
                "$set": {
                    "classroom": event["classroom"],
                    "building": event["building"],
                    "has_to_be_allocated": False,
                    "updated_at": now
                }
            }
            events.update_one(filter, query)

        for event in unallocated_events:
            filter = {
                "subject_code": event["subject_code"],
                "class_code": event["class_code"],
                "week_day": event["week_day"],
                "start_time": event["start_time"],
                "created_by": username,
            }

            query = {
                "$unset": {
                    "building": "",
                    "classroom": "",
                },
                "$set": {
                    "has_to_be_allocated": True,
                    "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
                },
            }
            events.update_one(filter, query)

        return dumps(result)

    except ValidationError as err:
        return {"message": err.messages}, 400

    except Exception as ex:
        return {"message": "Erro ao carregar alocação", "error": str(ex)}, 500


@event_blueprint.route("edit-allocations", methods=["PATCH"])
def edit_allocations():
    try:
        username = request.user.get("Username")
        allocated_events = request.json["allocated_events"]
        unallocated_events = request.json["unallocated_events"]

        filter = {"created_by": username}
        query = {
            "$set": {
                "allocated_events": allocated_events,
                "unallocated_events": unallocated_events,
                "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
            }
        }

        result = allocations.update_one(filter, query)
        return dumps(result.matched_count)

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500


@event_blueprint.route("edit/<subject_code>/<class_code>", methods=["PATCH"])
@swag_from(f"{yaml_files}/edit_allocation.yml")
def edit_class_allocation(subject_code, class_code):
    try:
        week_days = request.json
        classroom = request.args["classroom"]
        building = request.args["building"]
        username = request.user.get("Username")
        now = datetime.now().strftime("%d/%m/%Y %H:%M")

        filter = {
            "subject_code": subject_code,
            "class_code": class_code,
            "week_day": {"$in": week_days},
            "created_by": username,
        }

        query = {
            "$set": {
                "has_to_be_allocated": False,
                "classroom": classroom,
                "building": building,
                "updated_at": now,
            }
        }

        result = events.update_many(filter, query)

        return dumps(result.matched_count)

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500


@event_blueprint.route("delete/<subject_code>/<class_code>/<week_day>/<start_time>", methods=["PATCH"])
def delete_one_allocation(subject_code, class_code, week_day, start_time):
    try:
        username = request.user.get("Username")
        filter = {
            "created_by": username,
            "subject_code": subject_code,
            "class_code": class_code,
            "week_day": week_day,
            "start_time": start_time,
        }
        query = {
            "$unset": {
                "building": "",
                "classroom": "",
            },
            "$set": {
                "has_to_be_allocated": True,
                "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
            },
        }
        result = events.update_one(filter, query)

        if not result:
            raise PyMongoError(
                f"{subject_code} - {class_code} at {week_day} - {start_time} not found")
        return dumps(result.matched_count)

    except PyMongoError as err:
        return {"message": err._message}, 404

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500


@event_blueprint.route("delete/<subject_code>/<class_code>", methods=["PATCH"])
def delete_allocation(subject_code, class_code):
    try:
        username = request.user.get("Username")
        filter = {"created_by": username,
                  "subject_code": subject_code, "class_code": class_code}
        query = {
            "$unset": {
                "building": "",
                "classroom": "",
            },
            "$set": {
                "has_to_be_allocated": True,
                "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
            },
        }
        result = events.update_many(filter, query)
        if not result:
            raise PyMongoError(f"{subject_code} - {class_code} not found")
        return dumps(result.matched_count)

    except PyMongoError as err:
        return {"message": err._message}, 404

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500


@event_blueprint.route("delete-allocations", methods=["PATCH"])
def delete_all_allocations():
    try:
        username = request.user.get("Username")
        result = events.update_many(
            {"created_by": username},
            {
                "$unset": {
                    "building": "",
                    "classroom": "",
                },
                "$set": {
                    "has_to_be_allocated": True,
                    "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
                },
            },
        )
        return dumps(result.matched_count)

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500


@event_blueprint.route("/update-activeness", methods=["POST"])
def update_activeness():
    try:
        thread = Thread(target=update_events_activeness, args=(events,))
        thread.daemon = True
        thread.start()

        return dumps({"message": "Activeness was updated sucessfully!"})
    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500
