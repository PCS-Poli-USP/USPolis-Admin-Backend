from fastapi import APIRouter, Body
from server.deps.session_dep import SessionDep
from server.models.http.responses.occupance_reports_response import OccupanceReportsResponse
from server.services.occupance_reports_service import OccupanceReportsService

embed = Body(..., embed=True)

router = APIRouter(prefix="/buildings", tags=["Buildings"])

@router.get("/occupance_reports/{building_id}", response_model=list[OccupanceReportsResponse])
def get_reports(
    session: SessionDep,
    building_id: int,
):
    return OccupanceReportsService.get_occupance_reports(session = session, building_id = building_id)
