from datetime import datetime
import os

from bson import json_util
from bson.objectid import ObjectId
from flask import Blueprint, Response, jsonify, request
from src.common.database import database
from src.common.cache import cache

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

mobile_blueprint = Blueprint("mobile", __name__, url_prefix="/api/mobile")

events = database["events"]
classrooms = database["classrooms"]
comments = database["comments"]
programs = database["programs"]
institutional_events = database["institutional_events"]

events_aggregation = [
        {
            "$group": {
                "_id": {
                    "class_code": "$class_code",
                    "subject_code": "$subject_code",
                    "subject_name": "$subject_name",
                    "professor": "$professor",
                    "start_period": "$start_period",
                    "end_period": "$end_period",
                    "created_by": "$created_by",
                    "is_active": "$is_active"
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
    sorted_results = sorted(results, key=lambda x: (x.get("_id").get("subject_code"), x.get("_id").get("class_code")))
    
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


def map_periods(programs):
    for program in programs:
        program["periods"] = list(set((program.get("periods"))))
        program["program"] = program.get("_id")
        program["id"] = str(program.get("program_id")[0])
        del program["_id"]
        del program["program_id"]

    return sorted(programs, key=lambda x: (x.get("program")))


@mobile_blueprint.route("/classes", methods=["GET"])
@cache.cached()
def get_classes():
    new_aggregation = [
        {
            "$match": {
                "is_active": True,
            }
        },
        events_aggregation[0]
    ]
    result = events.aggregate(pipeline=new_aggregation)
    response = list(result)
    formatted_response = map_results(response)
    return Response(json_util.dumps(formatted_response), mimetype="application/json")


@mobile_blueprint.route("/comments", methods=["POST"])
def post_comment():
    try:
        email = request.json.get("email")
        comment = request.json.get("comment")

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


@mobile_blueprint.route("/programs", methods=["GET"])
@cache.cached()
def get_programs():
    pipeline = [
        {
            "$group": {
                "_id": "$text",
                "program_id": {"$addToSet": "$_id"},
                "periods": {"$addToSet": "$subjects.period"}
            }
        },
        {
            "$unwind": "$periods"
        },
    ]

    results = programs.aggregate(pipeline)
    mapped_response = map_periods(list(results))

    return jsonify(mapped_response)


@mobile_blueprint.route("/programs/classes", methods=["GET"])
def get_classes_by_program_and_period():

    period = int(request.args.get("period"))
    try:
        program = ObjectId(request.args.get("program"))
    except:
        return jsonify([])

    document = programs.find_one({"_id": program})
    
    if document:
        subjects_in_period = [subject for subject in document['subjects'] if subject['period'] == period]
        for subject in subjects_in_period:
            subject_code = subject.get("code")
            new_aggregation = [
                {
                    "$match": {
                        "is_active": True,
                        "subject_code": subject_code
                    }
                },
                events_aggregation[0]
            ]
            result = events.aggregate(pipeline=new_aggregation)
            response = list(result)
            formatted_response = map_results(response)
            subject["classes"] = formatted_response

        return Response(json_util.dumps(subjects_in_period), mimetype="application/json")
    else:
        return jsonify([])


@mobile_blueprint.route("/institutional-events", methods=["GET"])
def list_institutional_events():

    today_date = str(datetime.now().date())

    try:
        pipeline = [
            {
                '$addFields': {
                    'parsed_start_date': {
                        '$dateFromString': {
                            'dateString': {
                                '$substr': ['$start_datetime', 0, 10]
                            },
                            'format': "%Y-%m-%d"
                        }
                    }
                }
            },
            {
                '$match': {
                    'end_datetime': {
                        '$gte': today_date
                    }
                }
            },
            {
                '$sort': {
                    'parsed_start_date': 1,
                    'likes': -1
                }
            },
            {
                '$project': {
                    'parsed_start_date': 0
                }
            }
        ]
        response = institutional_events.aggregate(pipeline)
        return jsonify(list(response))

    except Exception as err:
        print(err)
        return jsonify({"detail": "Não foi possível listar os eventos!"}), 400



@mobile_blueprint.route("/institutional-events/<event_id>/like", methods=["PATCH"])
def like_institutional_event(event_id):
    """
    Like institutional event by ID
    """
    try:
        event = institutional_events.find_one({"_id": ObjectId(event_id)})
        if not event:
            return jsonify({"detail": "Evento não encontrado!"}), 404

        event["likes"] = event["likes"] + 1

        institutional_events.update_one({"_id": ObjectId(event_id)}, {"$set": event})

        return jsonify(event)

    except Exception as err:
        print(err)
        return jsonify({"detail": "Não foi possível curtir o evento!"}), 400


@mobile_blueprint.route("/institutional-events/<event_id>/remove-like", methods=["PATCH"])
def remove_like_on_institutional_event(event_id):
    """
    Remove like on institutional event by ID
    """
    try:
        event = institutional_events.find_one({"_id": ObjectId(event_id)})
        if not event:
            return jsonify({"detail": "Evento não encontrado!"}), 404

        event["likes"] = event["likes"] - 1

        institutional_events.update_one({"_id": ObjectId(event_id)}, {"$set": event})

        return jsonify(event)

    except Exception as err:
        print(err)
        return jsonify({"detail": "Não foi possível remover a curtida no evento!"}), 400
