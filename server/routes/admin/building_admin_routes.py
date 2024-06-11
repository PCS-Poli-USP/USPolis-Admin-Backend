from fastapi import APIRouter, Body, HTTPException, Response, status

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.building_request_models import (
    BuildingRegister,
    BuildingUpdate,
)
from server.models.http.responses.building_response_models import BuildingResponse
from server.models.http.responses.generic_responses import NoContent
from server.repositories.buildings_repository import BuildingRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/buildings", tags=["Buildings"])

@router.post("")
async def create_building(
    building_in: BuildingRegister,
    user: UserDep,
    session: SessionDep,
) -> BuildingResponse:
    """Create new building"""
    building = BuildingRepository.create(
        building_in=building_in, creator=user, session=session
    )
    return BuildingResponse.from_building(building)


@router.put("/{building_id}")
async def update_building(
    building_id: int, building_input: BuildingUpdate, session: SessionDep
) -> BuildingResponse:
    """Update a building"""
    building = BuildingRepository.get_by_id(id=building_id, session=session)
    building.name = building_input.name
    BuildingRepository.update(building=building, session=session)
    session.refresh(building)
    return BuildingResponse.from_building(building)


@router.delete("/{building_id}")
async def delete_building(building_id: int, session: SessionDep) -> Response:
    """Delete a building"""
    BuildingRepository.delete(building_id=building_id, session=session)
    return NoContent


class BuildingNameAlreadyExists(HTTPException):
    def __init__(self, building_name: str) -> None:
        super().__init__(
            status.HTTP_409_CONFLICT, f"Building {building_name} already exists"
        )
