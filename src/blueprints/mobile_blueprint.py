from datetime import datetime
import os

from bson import json_util
from flask import Blueprint, Response, jsonify, request
from src.common.database import database
from src.common.cache import cache

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

mobile_blueprint = Blueprint("mobile", __name__, url_prefix="/api/mobile")

events = database["events"]
classrooms = database["classrooms"]
comments = database["comments"]

def get_abbreviated_class_code(class_code):
    abbreviated_class_code = class_code[-2:]

    if abbreviated_class_code[0] == "0":
        return abbreviated_class_code[1]
    return abbreviated_class_code


def map_week_days(week_day):
    weekday_map = {
        "seg": "Segunda-feira",
        "ter": "Terça-feira",
        "qua": "Quarta-feira",
        "qui": "Quinta-feira",
        "sex": "Sexta-feira"
    }

    return weekday_map.get(week_day)


def find_floor(classroom_name, building):
    classroom = classrooms.find_one({"classroom_name": classroom_name, "building": building})
    return classroom.get("floor") if classroom is not None else None


def map_results(results):
    filtered_results = list(filter(lambda element: element.get("_id").get("created_by") == "amelia" or element.get("_id").get("created_by") == "eletrica-manual" or element.get("_id").get("created_by") == "producao-manual" or element.get("_id").get("created_by") == "civil-manual", results))
    sorted_results = sorted(filtered_results, key=lambda x: (x.get("_id").get("subject_code"), x.get("_id").get("class_code")))
    
    mapped_results = []
    for result in sorted_results:
        mapped_result = {
            **result.get("_id"),
            'id': f"{result.get('_id').get('subject_code')}_{result.get('_id').get('class_code')}",
            'class_code': get_abbreviated_class_code(result.get("_id").get("class_code")),
            'schedule': []
        }
        for day in result.get("schedule"):
            mapped_day = {
                **day,
                'week_day': map_week_days(day.get("week_day")),
                'floor': find_floor(day.get("classroom"), day.get("building"))
            }
            mapped_result['schedule'].append(mapped_day)
        mapped_results.append(mapped_result)
    
    return mapped_results


def send_email(comment: str, email: str = None):
    email_message = Mail(
        to_emails="uspolis@usp.br",
        from_email="uspolis@usp.br",
        subject="Comentário no app USPolis",
        html_content=f"""
            <p>Email: {email if email else "Não informado"}</p>
            <p>Comentário: {comment}</p>
        """
    )

    try:
        api_key = os.environ.get("SENDGRID_API_KEY")
        email_client = SendGridAPIClient(api_key)
        email_client.send(email_message)
        print("E-mail enviado com sucesso!")

    except Exception as err:
        print(f"Erro no envio de email: {err}")


@mobile_blueprint.route("/classes")
@cache.cached()
def get_classes():
    aggregation = [
        {
            "$group": {
                "_id": {
                    "class_code": "$class_code",
                    "subject_code": "$subject_code",
                    "subject_name": "$subject_name",
                    "professor": "$professor",
                    "start_period": "$start_period",
                    "end_period": "$end_period",
                    "created_by": "$created_by"
                },
                "schedule": {
                    "$push": {
                        "id": "$_id",
                        "week_day": "$week_day",
                        "start_time": "$start_time",
                        "end_time": "$end_time",
                        "building": "$building",
                        "classroom": "$classroom",
                    },
                },
            },
        },
    ]
    result = events.aggregate(pipeline=aggregation)
    response = list(result)
    formatted_response = map_results(response)
    return Response(json_util.dumps(formatted_response), mimetype="application/json")


@mobile_blueprint.route("/comments", methods=["POST"])
def post_comment():
    try:
        email = request.json["email"]
        comment = request.json["comment"]

        comment_doc = {
            "email": email,
            "comment": comment,
            "created_at": datetime.now().isoformat()
        }

        comments.insert_one(comment_doc)

        send_email(comment, email)

        return jsonify({"email": email, "comment": comment})

    except Exception as err:
        print(err)
        return jsonify({"detail": "Não foi possível inserir seu comentário!"}), 400
