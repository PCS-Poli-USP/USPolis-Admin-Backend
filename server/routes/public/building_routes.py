from fastapi import APIRouter

from server.models.database.building_db_model import Building
from server.models.http.responses.building_response_models import BuildingResponse

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.get("")
async def get_all_buildings() -> list[BuildingResponse]:
    """Get all buildings"""
    return await BuildingResponse.from_building_list(
        await Building.find_all().to_list()
    )


@router.get("/{building_id}")
async def get_building(building_id: str) -> BuildingResponse:
    """Get a building"""
    building = await Building.by_id(building_id)
    return await BuildingResponse.from_building(building)
