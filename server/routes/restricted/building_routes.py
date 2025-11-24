from fastapi import APIRouter, Body

from server.deps.repository_adapters.building_repository_adapter import (
    BuildingRepositoryDep,
)
from server.deps.session_dep import SessionDep
from server.models.database.building_db_model import Building
from server.models.http.responses.building_response_models import BuildingResponse
from server.models.http.responses.occupance_reports_response import OccupanceReportsResponse
from server.services.occupance_reports_service import OccupanceReportsService

embed = Body(..., embed=True)

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.get("/{building_id}")
def get_building_by_id(
    building_id: int, repository: BuildingRepositoryDep
) -> BuildingResponse:
    """Get a building by id"""
    building: Building = repository.get_by_id(id=building_id)
    return BuildingResponse.from_building(building)

@router.get("/occupance_reports/{building_id}", response_model=list[OccupanceReportsResponse])
def get_reports(
    session: SessionDep,
    building_id: int,
):
    return OccupanceReportsService.get_occupance_reports(session = session, building_id = building_id)
