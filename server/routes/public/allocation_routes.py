from datetime import date
from fastapi import APIRouter

from server.cache import date_range_cache
from server.deps.interval_dep import ensure_valid_span
from server.deps.session_dep import SessionDep
from server.models.http.responses.allocation_response_models import (
    AllocationEventResponse,
    AllocationResourceResponse,
)
from server.repositories.building_repository import BuildingRepository
from server.repositories.occurrence_repository import OccurrenceRepository
from server.repositories.schedule_repository import ScheduleRepository
from server.utils.brazil_datetime import BrazilDatetime


router = APIRouter(prefix="/allocations", tags=["Allocations"])

MAX_ALLOCATION_EVENTS_DAYS = 31


@router.get("/events")
@date_range_cache(expire_seconds=60)
def get_all_allocation_events(
    session: SessionDep,
    start: date | None = None,
    end: date | None = None,
) -> list[AllocationEventResponse]:
    """Get all events in date interval [start, end], if not provided, it will return all events on current day"""
    # Defaults resolved per request: `date.today()` as a parameter default is
    # evaluated once, at import, and would freeze "today" at server start.
    today = BrazilDatetime.now_utc().date()
    start = start or today
    end = end or today
    # Occurrences are expanded per day, so this route gets a tighter cap than
    # MAX_INTERVAL_DAYS: production traffic never asked for more than 14 days.
    ensure_valid_span(start, end, max_days=MAX_ALLOCATION_EVENTS_DAYS)
    occurrences = OccurrenceRepository.get_all_on_interval_for_allocation(
        start, end, session
    )
    schedules = ScheduleRepository.get_all_unallocated_for_classes(session=session)
    events = AllocationEventResponse.from_occurrence_list(occurrences)
    events.extend(AllocationEventResponse.from_schedule_list(schedules))
    return events


@router.get("/resources")
def get_all_allocation_resources(
    session: SessionDep,
) -> list[AllocationResourceResponse]:
    buildings = BuildingRepository.get_all(session=session)
    resources = AllocationResourceResponse.from_building_list(buildings)
    resources.append(AllocationResourceResponse.unnallocated_building())
    resources.append(AllocationResourceResponse.unnallocated_classroom())
    return resources
