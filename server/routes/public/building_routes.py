from fastapi import APIRouter

from server.deps.session_dep import SessionDep
from server.models.database.building_db_model import Building
from server.repositories.buildings_repository import BuildingRepository

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.get("", response_model_by_alias=False)
async def get_all_buildings(session: SessionDep) -> list[Building]:
    """Get all buildings"""
    return BuildingRepository.get_all(session=session)


# @router.get("/{building_id}", response_model_by_alias=False)
# async def get_building(building_id: str) -> Building:
#     """Get a building"""
#     building: Building = await Building.by_id(building_id)
#     return building
