from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Body, Depends, status

from server.services.auth.authenticate import admin_authenticate
from server.models.database.user_db_model import User
from server.models.database.building_db_model import Building
from server.models.http.requests.building_request_models import BuildingRegister, BuildingUpdate

embed = Body(..., embed=True)

router = APIRouter(
    prefix="/buildings", tags=["Buildings"], dependencies=[Depends(admin_authenticate)]
)


@router.get("")
async def get_all_buildings() -> list[Building]:
    """Get all buildings"""
    return await Building.find_all().to_list()


@router.get("/{building_id}")
async def get_building(building_id: str) -> Building:
    """Get a building"""
    return await Building.by_id(building_id)


@router.post("")
async def create_building(building_input: BuildingRegister, user: Annotated[User, Depends(admin_authenticate)]) -> str:
    """Create new building"""
    if await Building.check_name_exits(building_input.name):
        raise BuildingNameAlreadyExists(building_input.name)

    new_building = Building(
        name=building_input.name,
        created_by=user,
        updated_at=datetime.now()
    )
    await new_building.create()
    return str(new_building.id)


@router.patch("/{building_id}")
async def update_building(building_id: str, building_input: BuildingUpdate, user: Annotated[User, Depends(admin_authenticate)]) -> str:
    """Update a building"""
    building = await Building.by_id(building_id)
    building.name = building_input.name
    building.updated_at = datetime.now()
    await building.save()
    return building_id


@router.delete("/{building_id}")
async def delete_building(building_id: str, user: Annotated[User, Depends(admin_authenticate)]) -> int:
    """Delete a building"""
    building = await Building.by_id(building_id)
    response = await building.delete()
    if response is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "No building deleted")
    return int(response.deleted_count)


class BuildingNameAlreadyExists(HTTPException):
    def __init__(self, building_name: str) -> None:
        super().__init__(status.HTTP_409_CONFLICT,
                         f"Building {building_name} already exists")
