from fastapi import APIRouter, Body

from server.deps.repository_adapters.building_repository_adapter import (
    BuildingRepositoryDep,
)
from server.models.database.building_db_model import Building
from server.models.http.responses.building_response_models import BuildingResponse

embed = Body(..., embed=True)

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.get("/{building_id}")
def get_building_by_id(
    building_id: int, repository: BuildingRepositoryDep
) -> BuildingResponse:
    """Get an building by id"""
    building: Building = repository.get_by_id(id=building_id)
    return BuildingResponse.from_building(building)
