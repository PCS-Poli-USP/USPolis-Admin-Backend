from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status

from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User
from server.models.http.requests.building_request_models import (
    BuildingRegister,
    BuildingUpdate,
)
from server.services.auth.authenticate import authenticate

embed = Body(..., embed=True)

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.post("")
async def create_building(
    building_input: BuildingRegister, user: Annotated[User, Depends(authenticate)]
) -> str:
    """Create new building"""
    if await Building.check_name_exits(building_input.name):
        raise BuildingNameAlreadyExists(building_input.name)

    new_building = Building(
        name=building_input.name,
        created_by=user,  # type: ignore
        updated_at=datetime.now(),
    )
    await new_building.create()
    return str(new_building.id)


@router.put("/{building_id}")
async def update_building(building_id: str, building_input: BuildingUpdate) -> str:
    """Update a building"""
    if not await Building.check_name_is_valid(building_id, building_input.name):
        raise BuildingNameAlreadyExists(building_input.name)
    building = await Building.by_id(building_id)
    building.name = building_input.name
    building.updated_at = datetime.now()
    await building.save()  # type: ignore
    return building_id


@router.delete("/{building_id}")
async def delete_building(building_id: str) -> int:
    """Delete a building"""
    building = await Building.by_id(building_id)
    response = await building.delete()  # type: ignore
    if response is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "No building deleted"
        )
    return int(response.deleted_count)


class BuildingNameAlreadyExists(HTTPException):
    def __init__(self, building_name: str) -> None:
        super().__init__(
            status.HTTP_409_CONFLICT, f"Building {building_name} already exists"
        )
