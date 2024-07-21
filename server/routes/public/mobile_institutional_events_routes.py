from fastapi import APIRouter, Body

from server.deps.session_dep import SessionDep
from server.models.database.institutional_event_db_model import InstitutionalEvent
from server.repositories.institutional_event_repository import (
    InstitutionalEventRepository,
)
from server.routes.public.dtos.mobile_institutional_event_response import MobileInstitutionalEventLike, MobileInstitutionalEventResponse, to_event_update

embed = Body(..., embed=True)

router = APIRouter(prefix="/mobile/institutional-events", tags=["Mobile", "Institutional Events"])


@router.get("")
async def get_all_institutional_events(
    session: SessionDep,
) -> list[MobileInstitutionalEventResponse]:
    """Get all institutional events"""
    events = InstitutionalEventRepository.get_all(session=session)
    return MobileInstitutionalEventResponse.from_institutional_event_list(events)

@router.patch("")
async def handle_institutional_event_like(
    input: MobileInstitutionalEventLike,
    session: SessionDep
) -> MobileInstitutionalEventResponse:
    """Either like or dislike an institutional event, based on the user_id"""
    event: InstitutionalEvent = InstitutionalEventRepository.get_by_id(id=input.event_id, session=session)
    #TODO: add a real logic with database to process likes (after User and auth is created)
    if input.like: 
        event.likes += 1 
    elif event.likes > 0:
        event.likes -= 1 
    InstitutionalEventRepository.update(
        id=event.id, input=to_event_update(event), session=session)
    return event
