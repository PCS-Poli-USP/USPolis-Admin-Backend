from fastapi import APIRouter, Body, Query
from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.responses.occupance_reports_response import (
    OccupanceReportsResponse,
)
from server.services.occupance_reports_service import OccupanceReportsService
from server.services.security.buildings_permission_checker import (
    BuildingPermissionChecker,
)
from datetime import date

embed = Body(..., embed=True)

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.get("/occupance_reports/{building_id}")
def get_reports(
    building_id: int,
    user: UserDep,
    session: SessionDep,
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
)-> list[OccupanceReportsResponse]:
    authorization = BuildingPermissionChecker(user=user, session=session)
    authorization.check_permission(building_id)
    reports = OccupanceReportsService.get_occupance_reports(
        session=session, building_id=building_id, start_date = start_date, end_date = end_date
    )
    return OccupanceReportsResponse.from_dicts(reports)
    