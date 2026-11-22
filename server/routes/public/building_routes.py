from fastapi import APIRouter, Body

from server.deps.session_dep import SessionDep
from server.models.http.responses.building_response_models import BuildingResponse
from server.repositories.building_repository import BuildingRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.get("")
async def get_all_buildings(session: SessionDep) -> list[BuildingResponse]:
    """Get all buildings"""
    buildings = BuildingRepository.get_all(session=session)
    return BuildingResponse.from_building_list(buildings)
