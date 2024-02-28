from datetime import datetime

from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import request

from src.blueprints.blueprint_builder import build_authenticated_blueprint
from src.common.crawler import JupiterCrawler
from src.common.database import database
from src.repository.building_repository import BuildingRepository
from src.repository.user_repository import UserRepository

crawler_blueprint = build_authenticated_blueprint("crawler", "/api/crawl")

user_repository = UserRepository()
buildings_repository = BuildingRepository()
events_tb = database["events"]


@crawler_blueprint.post("")
def crawl_subject():
    username = request.user.get("Username")
    logged_user = user_repository.get_by_username(username)
    if logged_user is None:
        return {"message": "User not found"}, 404

    logged_user_building_ids = [
        str(building["_id"]) for building in logged_user["buildings"]
    ]
    logged_user_is_admin = user_repository.is_admin(username)

    payload = request.json
    if payload is None:
        return {"message": "body required"}, 400
    subject_codes_list = payload["subject_codes_list"]
    building_id = payload["building_id"]

    if building_id not in logged_user_building_ids and not logged_user_is_admin:
        return {"message": "You don't have permission to access this building"}, 403
    building = buildings_repository.get_by_id(building_id)
    if building is None:
        return {"message": "Building not found"}, 404

    updated = []
    inserted = []
    failed = []
    success = []
    for subject_code in subject_codes_list:
        try:
            events = JupiterCrawler.crawl_subject_static(subject_code)
            for event in events:
                event["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                event["created_by"] = username
                event["has_to_be_allocated"] = True
                event["ignore_to_allocate"] = False
                event["building"] = building["name"]

                event["preferences"] = {
                    "building_id": ObjectId(building_id),
                    "air_conditioning": False,
                    "projector": False,
                    "accessibility": False,
                }

                query = {
                    "class_code": event["class_code"],
                    "subject_code": event["subject_code"],
                    "week_day": event["week_day"],
                    "start_time": event["start_time"],
                }
                result = events_tb.update_one(
                    query, {"$set": event}, upsert=True)
                updated.append(
                    event["subject_code"]
                ) if result.matched_count else inserted.append(event["subject_code"])

            success.append(event["subject_code"])

        except Exception as e:
            failed.append(subject_code)

    return dumps({"updated": updated, "inserted": inserted, "sucess": success, "failed": failed})
