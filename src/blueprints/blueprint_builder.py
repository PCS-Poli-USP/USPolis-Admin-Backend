from flask.blueprints import Blueprint

from src.middlewares.auth_middleware import admin_middleware, auth_middleware


def build_authenticated_blueprint(name: str, endpoint: str) -> Blueprint:
    blueprint = Blueprint(name, __name__, url_prefix=endpoint)
    blueprint.before_request(auth_middleware)
    return blueprint


def build_admin_blueprint(name: str, endpoint: str) -> Blueprint:
    blueprint = build_authenticated_blueprint(name, endpoint)
    blueprint.before_request(admin_middleware)
    return blueprint
