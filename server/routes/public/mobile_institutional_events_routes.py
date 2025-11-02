from fastapi import APIRouter, Body

from server.deps.session_dep import SessionDep
from server.models.database.institutional_event_db_model import InstitutionalEvent
from server.repositories.institutional_event_repository import (
    InstitutionalEventRepository,
)
from server.models.http.responses.mobile_institutional_event_response_models import (
    MobileInstitutionalEventLike,
    MobileInstitutionalAllocationEventResponse,
    to_event_update,
)
from server.utils.must_be_int import must_be_int

embed = Body(..., embed=True)

router = APIRouter(
    prefix="/mobile/institutional-events", tags=["Mobile", "Institutional Events"]
)


@router.get("")
async def get_all_institutional_events(
    session: SessionDep,
) -> list[MobileInstitutionalAllocationEventResponse]:
    """Get all institutional events"""
    events = InstitutionalEventRepository.get_all(session=session)
    return MobileInstitutionalAllocationEventResponse.from_institutional_event_list(
        events
    )


@router.patch("")
async def handle_institutional_event_like(
    input: MobileInstitutionalEventLike, session: SessionDep
) -> MobileInstitutionalAllocationEventResponse:
    """Either like or dislike an institutional event, based on the user_id"""
    event: InstitutionalEvent = InstitutionalEventRepository.get_by_id(
        id=input.event_id, session=session
    )
    # TODO: add a real logic with database to process likes (after User and auth is created)
    if input.like:
        event.likes += 1
    elif event.likes > 0:
        event.likes -= 1
    InstitutionalEventRepository.update(
        id=must_be_int(event.id), input=to_event_update(event), session=session
    )
    return MobileInstitutionalAllocationEventResponse.from_model(event)
