from fastapi import APIRouter, Body

from server.deps.repository_adapters.building_repository_adapter import (
    BuildingRespositoryAdapterDep,
)
from server.models.database.building_db_model import Building
from server.models.http.responses.building_response_models import BuildingResponse
from server.repositories.building_repository import BuildingRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.get("")
async def get_all_buildings(
    repository: BuildingRespositoryAdapterDep,
) -> list[BuildingResponse]:
    """Get all buildings"""
    buildings = repository.get_all()
    return BuildingResponse.from_building_list(buildings)


@router.get("/{building_id}")
async def get_building(
    building_id: int, repository: BuildingRespositoryAdapterDep
) -> BuildingResponse:
    """Get an building by id"""
    building: Building = repository.get_by_id(id=building_id)
    return BuildingResponse.from_building(building)
