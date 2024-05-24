from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status

from server.deps.authenticate import authenticate
from server.deps.session_dep import SessionDep
from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User
from server.models.http.requests.building_request_models import (
    BuildingRegister,
)
from server.repositories.buildings_repository import BuildingRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.post("")
async def create_building(
    building_in: BuildingRegister,
    user: Annotated[User, Depends(authenticate)],
    session: SessionDep,
) -> Building:
    """Create new building"""
    building = BuildingRepository.create(
        building_in=building_in, creator=user, session=session
    )
    return building


# @router.put("/{building_id}")
# async def update_building(building_id: str, building_input: BuildingUpdate) -> str:
#     """Update a building"""
#     if not await Building.check_name_is_valid(building_id, building_input.name):
#         raise BuildingNameAlreadyExists(building_input.name)
#     building = await Building.by_id(building_id)
#     building.name = building_input.name
#     building.updated_at = datetime.now()
#     await building.save()  # type: ignore
#     return building_id


# @router.delete("/{building_id}")
# async def delete_building(building_id: str) -> int:
#     """Delete a building"""
#     building = await Building.by_id(building_id)
#     response = await building.delete()  # type: ignore
#     if response is None:
#         raise HTTPException(
#             status.HTTP_500_INTERNAL_SERVER_ERROR, "No building deleted"
#         )
#     return int(response.deleted_count)


class BuildingNameAlreadyExists(HTTPException):
    def __init__(self, building_name: str) -> None:
        super().__init__(
            status.HTTP_409_CONFLICT, f"Building {building_name} already exists"
        )
