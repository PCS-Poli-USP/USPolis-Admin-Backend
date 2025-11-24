from fastapi import APIRouter

from server.deps.interval_dep import QueryIntervalDep
from server.deps.session_dep import SessionDep
from server.models.http.responses.event_response_models import EventResponse
from server.repositories.event_repository import EventRepository


router = APIRouter(prefix="/events", tags=["Reservations", "Events"])


@router.get("")
def get_all_events(
    session: SessionDep, interval: QueryIntervalDep
) -> list[EventResponse]:
    events = EventRepository.get_all(session=session, interval=interval)
    return EventResponse.from_events(events)
