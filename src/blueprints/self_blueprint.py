from bson.json_util import dumps
from flask import Blueprint, request

from src.common.utils.prettify_id import prettify_id, recursive_prettify_id
from src.middlewares.auth_middleware import auth_middleware
from src.repository.user_repository import UserRepository

self_blueprint = Blueprint("self", __name__, url_prefix="/api/self")
user_repository = UserRepository()


@self_blueprint.before_request
def _():
    return auth_middleware()


@self_blueprint.get("")
def get_user():
    user = user_repository.get_by_username(request.user.get("Username"))
    recursive_prettify_id(user)
    return dumps(user)
