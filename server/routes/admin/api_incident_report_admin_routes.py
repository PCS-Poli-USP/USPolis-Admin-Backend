from fastapi import APIRouter, Query, status

from server.deps.pagination_dep import PaginationDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.api_incident_report_request_models import (
    ApiIncidentReportCreateRequest,
    ApiIncidentReportStatusUpdateRequest,
)
from server.models.http.responses.api_incident_report_response import (
    ApiIncidentReportResponse,
)
from server.models.http.responses.paginated_response_models import PaginatedResponse
from server.repositories.api_incident_report_repository import (
    ApiIncidentReportRepository,
)
from server.utils.enums.incident_report_enums import (
    IncidentReportLevel,
    IncidentReportStatus,
)

router = APIRouter(prefix="/api-incident-reports", tags=["API Incident Reports"])


@router.get("")
def get_api_incident_reports_paginated(
    pagination: PaginationDep,
    session: SessionDep,
    status: IncidentReportStatus | None = Query(default=None),
    level: IncidentReportLevel | None = Query(default=None),
) -> PaginatedResponse[ApiIncidentReportResponse]:
    paginated_result = ApiIncidentReportRepository.get_all_paginated(
        pagination=pagination, status=status, level=level, session=session
    )
    return PaginatedResponse[ApiIncidentReportResponse](
        page=paginated_result.page,
        page_size=paginated_result.page_size,
        total_items=paginated_result.total_items,
        total_pages=paginated_result.total_pages,
        data=ApiIncidentReportResponse.from_incident_list(paginated_result.items),
    )


@router.get("/{incident_id}")
def get_api_incident_report(
    incident_id: int, session: SessionDep
) -> ApiIncidentReportResponse:
    incident = ApiIncidentReportRepository.get_by_id(id=incident_id, session=session)
    return ApiIncidentReportResponse.from_incident(incident)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_api_incident_report(
    input: ApiIncidentReportCreateRequest, session: SessionDep
) -> ApiIncidentReportResponse:
    incident = ApiIncidentReportRepository.create(
        access_log_id=input.access_log_id,
        level=input.level,
        description=input.description,
        session=session,
    )
    session.commit()
    return ApiIncidentReportResponse.from_incident(incident)


@router.patch("/{incident_id}/status")
def update_api_incident_report_status(
    incident_id: int,
    input: ApiIncidentReportStatusUpdateRequest,
    session: SessionDep,
) -> ApiIncidentReportResponse:
    incident = ApiIncidentReportRepository.get_by_id(id=incident_id, session=session)
    ApiIncidentReportRepository.update_status(
        incident=incident, status=input.status, session=session
    )
    session.commit()
    return ApiIncidentReportResponse.from_incident(incident)
