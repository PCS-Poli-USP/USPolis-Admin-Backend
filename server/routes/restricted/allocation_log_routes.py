from fastapi import APIRouter

from server.deps.repository_adapters.schedule_repository_adapter import (
    ScheduleRepositoryDep,
)
from server.models.http.responses.allocation_log_response import AllocationLogResponse


router = APIRouter(prefix="/allocations_logs", tags=["AllocationsLogs"])


@router.get("/{schedule_id}")
def get_schedule_allocation_logs(
    schedule_id: int,
    repository: ScheduleRepositoryDep,
) -> list[AllocationLogResponse]:
    """Get all allocation logs for a schedule"""
    logs = repository.get_allocation_logs(schedule_id)
    return AllocationLogResponse.from_allocation_logs(logs)
