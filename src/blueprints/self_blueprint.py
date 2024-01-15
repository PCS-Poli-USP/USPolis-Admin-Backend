from flask import Blueprint, request
from datetime import datetime
from bson.json_util import dumps
from bson.objectid import ObjectId
from marshmallow import ValidationError
from pymongo.errors import DuplicateKeyError, PyMongoError
from src.common.utils.prettify_id import prettify_id, recursive_prettify_id
from src.common.database import database
from src.schemas.user_schemas import UserInputSchema
from src.middlewares.auth_middleware import auth_middleware
from src.repository.user_repository import UserRepository
from src.repository.building_repository import BuildingRepository
import src.services.user.user_services as user_services

self_blueprint = Blueprint("self", __name__, url_prefix="/api/self")
user_repository = UserRepository()


@self_blueprint.before_request
def _():
    return auth_middleware()


@self_blueprint.get("")
def get_user():
    user = user_repository.get_by_username(request.user.get("Username"))
    prettify_id(user)
    return dumps(user)
