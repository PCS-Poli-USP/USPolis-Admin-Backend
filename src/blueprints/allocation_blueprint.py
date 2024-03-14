from flask import request

from src.blueprints.blueprint_builder import build_authenticated_blueprint
from src.common.general_error import GeneralError
from src.common.utils.validate_body import validate_body
from src.repository.allocation_repository import AllocationRepository
from src.schemas.allocation_schema import UpdateManyAllocationsSchema, UpdateManyAllocationsInManyBuildingsSchema

allocation_blueprint = build_authenticated_blueprint(
    "allocations", "/api/allocations")


@allocation_blueprint.put("/update-many")
def update_allocations():
    schema = UpdateManyAllocationsSchema()
    allocationRepository = AllocationRepository()
    try:
        data = validate_body(request.json, schema)
        events_ids = data.get("events_ids")
        building_id = data.get("building_id")
        classroom = data.get("classroom")

        updated_count = allocationRepository.update_many_allocations(
            events_ids, building_id, classroom
        )
        return {"message": f"Updated {updated_count} allocations"}, 200

    except GeneralError as e:
        return e.get_tuple()
    except Exception as e:
        return {"message": str(e)}, 500


@allocation_blueprint.put("/update-many-in-many-buildings")
def update_allocations_in_many_buildings():
    schema = UpdateManyAllocationsInManyBuildingsSchema()
    allocationRepository = AllocationRepository()
    try:
        data = validate_body(request.json, schema)
        events_ids = data.get("events_ids")
        buildings_ids = data.get("buildings_ids")
        classrooms = data.get("classrooms")

        updated_count = allocationRepository.update_many_allocations_in_many_buildings(
            events_ids, buildings_ids, classrooms
        )
        return {"message": f"Updated {updated_count} allocations"}, 200

    except GeneralError as e:
        return e.get_tuple()
    except Exception as e:
        return {"message": str(e)}, 500


@allocation_blueprint.delete("/delete-many")
def delete_allocations():
    schema = UpdateManyAllocationsSchema()
    allocationRepository = AllocationRepository()
    try:
        data = validate_body(request.json, schema)
        events_ids = data.get("events_ids")

        updated_count = allocationRepository.delete_many_allocations(
            events_ids)
        return {"message": f"Updated {updated_count} allocations"}, 200

    except GeneralError as e:
        return e.get_tuple()
    except Exception as e:
        return {"message": str(e)}, 500
