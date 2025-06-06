from fastapi import APIRouter, Body, status
from fastapi.responses import JSONResponse

from server.deps.repository_adapters.building_repository_adapter import (
    BuildingRepositoryDep,
)
from server.models.http.requests.building_request_models import (
    BuildingRegister,
    BuildingUpdate,
)
from server.models.http.responses.building_response_models import BuildingResponse

embed = Body(..., embed=True)

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.post("")
def create_building(
    input: BuildingRegister, repository: BuildingRepositoryDep
) -> BuildingResponse:
    """Create new building"""
    building = repository.create(input=input)
    return BuildingResponse.from_building(building)


@router.put("/{building_id}")
def update_building(
    building_id: int, input: BuildingUpdate, repository: BuildingRepositoryDep
) -> BuildingResponse:
    """Update a building by id"""
    building = repository.update(id=building_id, input=input)
    return BuildingResponse.from_building(building)


@router.delete("/{building_id}")
def delete_building(
    building_id: int, repository: BuildingRepositoryDep
) -> JSONResponse:
    """Delete a building by id"""
    repository.delete(id=building_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Prédio removido com sucesso",
        },
    )
