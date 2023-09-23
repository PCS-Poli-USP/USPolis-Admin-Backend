from datetime import datetime

from flask import Blueprint, jsonify, request
from src.common.database import database

institutional_event_blueprint = Blueprint(
    "institutional_event", __name__, url_prefix="/api/institutional_events")

institutional_events = database["institutional_events"]


@institutional_event_blueprint.route("", methods=["POST"])
def create_institutional_event():
    """
    Create institutional event via Admin
    """
    try:
        title = request.json.get("title")
        description = request.json.get("description")
        start_datetime = request.json.get("start_datetime")
        end_datetime = request.json.get("end_datetime")
        location = request.json.get("location")
        building = request.json.get("building")
        classroom = request.json.get("classroom")
        external_link = request.json.get("external_link")
        category = request.json.get("category")

        event_doc = {
            "title": title,
            "description": description,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "location": location,
            "building": building,
            "classroom": classroom,
            "external_link": external_link,
            "category": category,
            "created_at": datetime.now().isoformat()
        }

        institutional_events.insert_one(event_doc)
        return jsonify(event_doc)

    except Exception as err:
        print(err)
        return jsonify({"detail": "Não foi possível inserir o novo evento!"}), 400
