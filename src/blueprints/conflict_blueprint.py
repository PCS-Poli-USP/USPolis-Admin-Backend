from bson.json_util import dumps
from flask import Blueprint, request

from src.blueprints.blueprint_builder import build_authenticated_blueprint
from src.repository.conflicts_repository import ConflictRepository

conflict_blueprint = build_authenticated_blueprint("conflicts", "/api/conflicts")


@conflict_blueprint.get("")
def get_conflicts():
    conflictRepository = ConflictRepository()
    try:
        confclits = conflictRepository.get_all()
        return dumps(confclits), 200
    except:
        return "Internal server error", 500
