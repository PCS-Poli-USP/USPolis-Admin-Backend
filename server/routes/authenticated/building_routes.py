from fastapi import APIRouter, Body

from server.deps.session_dep import SessionDep
from server.models.http.responses.building_response_models import BuildingResponse
from server.repositories.building_repository import BuildingRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.get("/{building_id}")
def get_building_by_id(building_id: int, session: SessionDep) -> BuildingResponse:
    """Get an building by id"""
    building = BuildingRepository.get_by_id(id=building_id, session=session)
    return BuildingResponse.from_building(building)
