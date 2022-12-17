from flask import Blueprint, request
from bson.json_util import dumps
from marshmallow import EXCLUDE, ValidationError
from datetime import datetime
from flasgger import swag_from

from src.common.database import database
from src.schemas.allocation_schema import AllocatorInputSchema, AllocatorOutputSchema
from src.common.allocation.allocator import allocate_classrooms

event_blueprint = Blueprint("events", __name__, url_prefix="/api/events")

events = database["events"]
classrooms = database["classrooms"]

# class id - class_code, subject_code
# event id - start_time, end_time, week_day
# classroom id - building, classroom

allocation_output_schema = AllocatorOutputSchema()
allocation_input_schema = AllocatorInputSchema(many=True, unknown=EXCLUDE)

yaml_files = "../swagger/events"

@event_blueprint.route("")
@swag_from(f"{yaml_files}/get_events.yml")
def get_events():
  username = request.headers.get('username')
  result = events.find({ "created_by" : username }, { "_id" : 0 })
  resultList = list(result)

  return dumps(resultList)


@event_blueprint.route("allocate", methods=["PATCH"])
@swag_from(f"{yaml_files}/save_new_allocation.yml")
def save_new_allocation():
  try:
    username = request.headers.get('username')
    classrooms_list = list(classrooms.find({ "created_by" : username }, { "_id" : 0 }))
    events_list = list(events.find({}, { "_id" : 0 }))

    # parse date & time fields
    allocation_input_schema_load = allocation_input_schema.load(events_list)

    print(f'Number of events: {len(events_list)}')

    # clear previous allocation
    events.update_many({}, { "$unset" : { "classroom" : True, "building" : True } })

    allocation_events = allocate_classrooms(classrooms_list, allocation_input_schema_load)
    allocated = 0

    for event in allocation_events:
      allocation_output_schema_load = allocation_output_schema.load(event)
      allocation_output_schema_load["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")

      query = {
        "class_code" : allocation_output_schema_load["class_code"],
        "subject_code" : allocation_output_schema_load["subject_code"],
        "week_day" : allocation_output_schema_load["week_day"],
        "created_by" : username
      }
      result = events.update_one(
        query,
        { "$set" : allocation_output_schema_load },
        upsert=True)

      allocated += result.matched_count

    return dumps({ "allocated" : allocated , "unallocated" : len(events_list) - allocated })

  except ValidationError as err:
    return { "message" : err.messages }, 400

  except Exception as ex:
    return { "message" : "Erro ao calcular alocação", "error": str(ex) }, 500


@event_blueprint.route("edit/<subject_code>/<class_code>", methods=["PATCH"])
@swag_from(f"{yaml_files}/edit_allocation.yml")
def edit_allocation(subject_code, class_code):
  try:
    week_days = request.json
    classroom = request.args["classroom"]
    building = request.args["building"]
    username = request.headers.get('username')

    query = {
        "subject_code" : subject_code,
        "class_code" : class_code,
        "week_day": { "$in" : week_days },
        "created_by" : username
      }

    result = events.update_many(query,
      { "$set" :
        { "classroom" : classroom,
          "building" : building,
          "updated_at" : datetime.now().strftime("%d/%m/%Y %H:%M") }
      }
    )

    return dumps(result.matched_count)

  except Exception as ex:
    print(ex)
    return { "message" : str(ex) }, 500
