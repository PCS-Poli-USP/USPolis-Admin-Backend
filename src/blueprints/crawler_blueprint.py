from datetime import datetime

from bson.json_util import dumps
from flask import request

from src.blueprints.blueprint_builder import build_authenticated_blueprint
from src.common.database import database
from src.common.new_crawler import JupiterCrawler
from src.repository.user_repository import UserRepository

crawler_blueprint = build_authenticated_blueprint("crawler", "/api/crawl")

user_repository = UserRepository()
jupiter_crawler = JupiterCrawler()
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

    updated = []
    inserted = []
    for subject_code in subject_codes_list:
        events = jupiter_crawler.crawl_subject(subject_code)
        for event in events:
            event["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            event["created_by"] = username
            event["subject_code"] = subject_code
            event["has_to_be_allocated"] = True

            event["preferences"] = {
                "building_id": building_id,
                "air_conditioning": False,
                "projector": False,
                "accessibility": False,
            }

            query = {
                "class_code": event["class_code"],
                "subject_code": event["subject_code"],
                "week_day": event["week_day"],
            }
            result = events_tb.update_one(query, {"$set": event}, upsert=True)
            updated.append(
                event["subject_code"]
            ) if result.matched_count else inserted.append(event["subject_code"])

    return dumps({"updated": updated, "inserted": inserted})
