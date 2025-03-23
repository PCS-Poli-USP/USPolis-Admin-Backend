from fastapi import APIRouter, Body, HTTPException, Response, status

from server.deps.repository_adapters.building_repository_adapter import (
    BuildingRespositoryAdapterDep,
)
from server.models.http.requests.building_request_models import (
    BuildingRegister,
    BuildingUpdate,
)
from server.models.http.responses.building_response_models import BuildingResponse
from server.models.http.responses.generic_responses import NoContent

embed = Body(..., embed=True)

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.post("")
def create_building(
    input: BuildingRegister, repository: BuildingRespositoryAdapterDep
) -> BuildingResponse:
    """Create new building"""
    building = repository.create(input=input)
    return BuildingResponse.from_building(building)


@router.put("/{building_id}")
def update_building(
    building_id: int, input: BuildingUpdate, repository: BuildingRespositoryAdapterDep
) -> BuildingResponse:
    """Update a building by id"""
    building = repository.update(id=building_id, input=input)
    return BuildingResponse.from_building(building)


@router.delete("/{building_id}")
def delete_building(
    building_id: int, repository: BuildingRespositoryAdapterDep
) -> Response:
    """Delete a building by id"""
    repository.delete(id=building_id)
    return NoContent


class BuildingNameAlreadyExists(HTTPException):
    def __init__(self, building_name: str) -> None:
        super().__init__(
            status.HTTP_409_CONFLICT,
            f"Prédio {building_name} já existe",
        )
