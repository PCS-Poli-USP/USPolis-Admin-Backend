from datetime import datetime, timedelta

from fastapi import APIRouter, Query

from server.config import CONFIG
from server.deps.pagination_dep import PaginationDep
from server.deps.session_dep import SessionDep
from server.models.http.responses.api_access_log_response import ApiAccessLogResponse
from server.models.http.responses.api_access_log_summary_response import (
    ApiAccessLogSummaryResponse,
    StatusCodeCount,
)
from server.models.http.responses.paginated_response_models import PaginatedResponse
from server.repositories.api_access_log_repository import ApiAccessLogRepository
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.api_security_level_enum import APISecurityLevel

router = APIRouter(prefix="/api-access-logs", tags=["API Access Logs"])


@router.get("")
def get_api_access_logs_paginated(
    pagination: PaginationDep,
    session: SessionDep,
    status_code: int | None = Query(default=None),
    method: str | None = Query(default=None),
    security_level: APISecurityLevel | None = Query(default=None),
    since: datetime | None = Query(default=None),
    until: datetime | None = Query(default=None),
) -> PaginatedResponse[ApiAccessLogResponse]:
    paginated_result = ApiAccessLogRepository.get_all_paginated(
        pagination=pagination,
        status_code=status_code,
        method=method,
        security_level=security_level,
        since=since,
        until=until,
        session=session,
    )
    return PaginatedResponse[ApiAccessLogResponse](
        page=paginated_result.page,
        page_size=paginated_result.page_size,
        total_items=paginated_result.total_items,
        total_pages=paginated_result.total_pages,
        data=ApiAccessLogResponse.from_access_log_list(paginated_result.items),
    )


@router.get("/summary")
def get_api_access_log_summary(
    session: SessionDep,
    days: int = Query(default=7, ge=1, le=CONFIG.error_metrics_retention_days),
) -> ApiAccessLogSummaryResponse:
    since = BrazilDatetime.now_utc() - timedelta(days=days)
    counts = ApiAccessLogRepository.get_summary(since=since, session=session)
    return ApiAccessLogSummaryResponse(
        since_days=days,
        total_errors=sum(c for _, c in counts),
        by_status_code=[
            StatusCodeCount(status_code=sc, count=c) for sc, c in counts
        ],
    )


@router.get("/{access_log_id}")
def get_api_access_log(access_log_id: int, session: SessionDep) -> ApiAccessLogResponse:
    access_log = ApiAccessLogRepository.get_by_id(id=access_log_id, session=session)
    return ApiAccessLogResponse.from_access_log(access_log)
