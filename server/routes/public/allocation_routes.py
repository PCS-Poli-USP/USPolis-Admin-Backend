from datetime import date
from fastapi import APIRouter

from server.deps.session_dep import SessionDep
from server.models.http.responses.allocation_response_models import EventResponse
from server.repositories.occurrence_repository import OccurrenceRepository
from server.repositories.schedule_repository import ScheduleRepository


router = APIRouter(prefix="/allocations", tags=["Allocations", "Public"])


@router.get("/events")
def get_all_allocation_events(
    session: SessionDep,
    start: date = date.today(),
    end: date = date.today(),
) -> list[EventResponse]:
    """Get all events in date interval [start, end], if not provided, it will return all events on current day"""
    occurrences = OccurrenceRepository.get_all_on_interval(start, end, session)
    schedules = ScheduleRepository.get_all_unallocated(session=session)
    events = EventResponse.from_occurrence_list(occurrences)
    events.extend(EventResponse.from_schedule_list(schedules))
    return events
