from bson.json_util import dumps

from src.blueprints.blueprint_builder import build_authenticated_blueprint
from src.common.utils.prettify_id import recursive_prettify_id
from src.repository.conflicts_repository import ConflictRepository

conflict_blueprint = build_authenticated_blueprint("conflicts", "/api/conflicts")


@conflict_blueprint.get("")
def get_conflicts():
    conflictRepository = ConflictRepository()
    try:
        conflicts = conflictRepository.get_all()
        recursive_prettify_id(conflicts)
        return dumps(conflicts), 200

    # TODO: handle exceptions
    except Exception as e:
        return {"message": str(e)}, 500
