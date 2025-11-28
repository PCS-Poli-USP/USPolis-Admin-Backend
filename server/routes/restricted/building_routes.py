from fastapi import APIRouter, Body
from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.responses.occupance_reports_response import (
    OccupanceReportsResponse,
)
from server.services.occupance_reports_service import OccupanceReportsService
from server.services.security.buildings_permission_checker import (
    BuildingPermissionChecker,
)

embed = Body(..., embed=True)

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.get("/occupance_reports/{building_id}")
def get_reports(
    building_id: int,
    user: UserDep,
    session: SessionDep,
) -> list[OccupanceReportsResponse]:
    authorization = BuildingPermissionChecker(user=user, session=session)
    authorization.check_permission(building_id)
    reports = OccupanceReportsService.get_occupance_reports(
        session=session, building_id=building_id
    )
    return OccupanceReportsResponse.from_dicts(reports)
