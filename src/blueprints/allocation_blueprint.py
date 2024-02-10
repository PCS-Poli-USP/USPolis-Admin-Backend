from flask import request

from src.blueprints.blueprint_builder import build_authenticated_blueprint
from src.common.general_error import GeneralError
from src.common.utils.validate_body import validate_body
from src.repository.allocation_repository import AllocationRepository
from src.schemas.allocation_schema import UpdateManyAllocationsSchema

allocation_blueprint = build_authenticated_blueprint("allocations", "/api/allocations")


@allocation_blueprint.put("/update-many")
def update_allocations():
    schema = UpdateManyAllocationsSchema()
    allocationRepository = AllocationRepository()
    try:
        data = validate_body(request.json, schema)
        events = data.get("events")
        updated_count = allocationRepository.update_many_allocations(events)
        return {"message": f"Updated {updated_count} allocations"}, 200

    except GeneralError as e:
        return e.get_tuple()
    except Exception as e:
        return {"message": str(e)}, 500
