from datetime import datetime
from bson import ObjectId

from flask import Blueprint, jsonify, request
from src.common.database import database

institutional_event_blueprint = Blueprint(
    "institutional_event", __name__, url_prefix="/api/institutional-events")

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


@institutional_event_blueprint.route("/<event_id>", methods=["PATCH"])
def update_institutional_event(event_id):
    """
    Update institutional event by ID
    """
    try:
        event = institutional_events.find_one({"_id": ObjectId(event_id)})
        if not event:
            return jsonify({"detail": "Evento não encontrado!"}), 404

        title = request.json.get("title")
        description = request.json.get("description")
        start_datetime = request.json.get("start_datetime")
        end_datetime = request.json.get("end_datetime")
        location = request.json.get("location")
        building = request.json.get("building")
        classroom = request.json.get("classroom")
        external_link = request.json.get("external_link")
        category = request.json.get("category")

        if title:
            event["title"] = title
        if description:
            event["description"] = description
        if start_datetime:
            event["start_datetime"] = start_datetime
        if end_datetime:
            event["end_datetime"] = end_datetime
        if location:
            event["location"] = location
        if building:
            event["building"] = building
        if classroom:
            event["classroom"] = classroom
        if external_link:
            event["external_link"] = external_link
        if category:
            event["category"] = category

        institutional_events.update_one({"_id": ObjectId(event_id)}, {"$set": event})

        return jsonify(event)

    except Exception as err:
        print(err)
        return jsonify({"detail": "Não foi possível atualizar o evento!"}), 400


@institutional_event_blueprint.route("/<event_id>", methods=["DELETE"])
def delete_institutional_event(event_id):
    """
    Delete institutional event by ID
    """
    try:
        event = institutional_events.find_one({"_id": ObjectId(event_id)})
        if not event:
            return jsonify({"detail": "Evento não encontrado!"}), 404

        institutional_events.delete_one({"_id": ObjectId(event_id)})

        return jsonify({"detail": "Evento deletado com sucesso!"})

    except Exception as err:
        print(err)
        return jsonify({"detail": "Não foi possível deletar o evento!"}), 400