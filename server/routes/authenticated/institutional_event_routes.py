from fastapi import APIRouter, Body

from server.deps.session_dep import SessionDep
from server.models.http.responses.institutional_event_response_models import (
    InstitutionalEventResponse,
)
from server.repositories.institutional_event_repository import (
    InstitutionalEventRepository,
)

embed = Body(..., embed=True)

router = APIRouter(prefix="/institutional_events", tags=["Institutional Events"])


@router.get("")
def get_all_institutional_events(
    session: SessionDep,
) -> list[InstitutionalEventResponse]:
    """Get all institutional events"""
    events = InstitutionalEventRepository.get_all(session=session)
    return InstitutionalEventResponse.from_institutional_event_list(events)


@router.get("/{institutional_event_id}")
def get_institutional_event(
    institutional_event_id: int, session: SessionDep
) -> InstitutionalEventResponse:
    """Get an institutional event by id"""
    event = InstitutionalEventRepository.get_by_id(
        id=institutional_event_id, session=session
    )
    return InstitutionalEventResponse.from_institutional_event(event)
