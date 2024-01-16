from flask import Blueprint, request
from bson.json_util import dumps
from marshmallow import EXCLUDE, ValidationError
from datetime import datetime, timedelta
from flasgger import swag_from
from threading import Thread

from src.common.tasks import update_events_activeness
from src.common.database import database
from src.schemas.allocation_schema import AllocatorInputSchema, AllocatorOutputSchema
from src.common.allocation.new_allocator import allocate_classrooms
from src.common.utils.classes.classes_sorter import sort_classes_by_vacancies
from src.common.utils.classroom.classroom_sorter import sort_classrooms_by_capacity
from src.common.utils.event.event_sorter import sort_events_by_subject_code
# from src.common.utils.event.events_formatter import clear_event_allocation
from src.middlewares.auth_middleware import auth_middleware

event_blueprint = Blueprint("events", __name__, url_prefix="/api/events")

events = database["events"]
classrooms = database["classrooms"]

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
    result = events.find({"created_by": username, "subject_code": subject_code, "class_code": class_code })
    resultList = list(result)
    return dumps(resultList)

@event_blueprint.route("allocate", methods=["PATCH"])
@swag_from(f"{yaml_files}/save_new_allocation.yml")
def save_new_allocation():
    try:
        username = request.user.get("Username")
        classroom_list = list(classrooms.find({"created_by": username}, {"_id": 0}))
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
                        "vacancies" : {"$first": "$vacancies"},
                        "pendings" : {"$first": "$pendings"},
                    }
                },
            ]
        )
        class_list = list(result)
        result = allocate_classrooms(classroom_list, class_list)
        allocated_classes = result[0]
        unallocated_classes = result[1]

        return {"allocated" : allocated_classes, "unallocated" : unallocated_classes}

    except ValidationError as err:
        return {"message": err.messages}, 400

    except Exception as ex:
        return {"message": "Erro ao calcular alocação", "error": str(ex)}, 500


@event_blueprint.route("edit/<subject_code>/<class_code>", methods=["PATCH"])
@swag_from(f"{yaml_files}/edit_allocation.yml")
def edit_allocation(subject_code, class_code):
    try:
        week_days = request.json
        classroom = request.args["classroom"]
        building = request.args["building"]
        username = request.user.get("Username")

        query = {
            "subject_code": subject_code,
            "class_code": class_code,
            "week_day": {"$in": week_days},
            "created_by": username,
        }

        result = events.update_many(
            query,
            {
                "$set": {
                    "has_to_be_allocated": False,
                    "classroom": classroom,
                    "building": building,
                    "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
                }
            },
        )

        return dumps(result.matched_count)

    except Exception as ex:
        print(ex)
        return {"message": str(ex)}, 500

@event_blueprint.route("delete-allocations", methods=["PATCH"])
def delete_allocations():
    try:
        username = request.user.get("Username")
        result = events.update_many(
            {"created_by" : username},
            {
                "$unset" : {
                    "building" : "", 
                    "classroom" : "",
                },
                "$set": { "has_to_be_allocated": True}
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
