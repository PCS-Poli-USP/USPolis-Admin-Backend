from fastapi import APIRouter

from server.models.database.building_db_model import Building

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.get("")
async def get_all_buildings() -> list[Building]:
    """Get all buildings"""
    return await Building.find_all().to_list()


@router.get("/{building_id}")
async def get_building(building_id: str) -> Building:
    """Get a building"""
    building: Building = await Building.by_id(building_id)
    return building
