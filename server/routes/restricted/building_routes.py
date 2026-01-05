from fastapi import APIRouter, Body, Query
from server.deps.session_dep import SessionDep
from server.models.http.responses.occupance_reports_response import OccupanceReportsResponse
from server.services.occupance_reports_service import OccupanceReportsService
from datetime import date

embed = Body(..., embed=True)

router = APIRouter(prefix="/buildings", tags=["Buildings"])

@router.get("/occupance_reports/{building_id}", response_model=list[OccupanceReportsResponse])
def get_reports(
    session: SessionDep,
    building_id: int,
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
):
    return OccupanceReportsService.get_occupance_reports(session = session, building_id = building_id, start_date = start_date, end_date = end_date)
