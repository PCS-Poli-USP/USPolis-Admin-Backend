from fastapi import APIRouter, Body, Response

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.institutional_event_request_models import (
    InstitutionalEventRegister,
    InstitutionalEventUpdate,
)
from server.models.http.responses.generic_responses import NoContent
from server.models.http.responses.institutional_event_response_models import (
    InstitutionalAllocationEventResponse,
)
from server.repositories.institutional_event_repository import (
    InstitutionalEventRepository,
)

embed = Body(..., embed=True)

router = APIRouter(prefix="/institutional_events", tags=["Institutional Events"])


@router.post("")
def create_institutional_event(
    institutional_event_input: InstitutionalEventRegister,
    user: UserDep,
    session: SessionDep,
) -> InstitutionalAllocationEventResponse:
    """Create an institutional event (the user is recorded as its creator)"""
    event = InstitutionalEventRepository.create(
        creator=user, input=institutional_event_input, session=session
    )
    return InstitutionalAllocationEventResponse.from_institutional_event(event)


@router.put("/{institutional_event_id}")
def update_institutional_event(
    institutional_event_id: int,
    institutional_event_input: InstitutionalEventUpdate,
    user: UserDep,
    session: SessionDep,
) -> InstitutionalAllocationEventResponse:
    """Update an institutional event by id (its creator or an admin)"""
    event = InstitutionalEventRepository.update(
        id=institutional_event_id,
        input=institutional_event_input,
        user=user,
        session=session,
    )
    return InstitutionalAllocationEventResponse.from_institutional_event(event)


@router.delete("/{institutional_event_id}")
def delete_institutional_event(
    institutional_event_id: int, user: UserDep, session: SessionDep
) -> Response:
    """Delete an institutional event by id (its creator or an admin)"""
    InstitutionalEventRepository.delete(
        id=institutional_event_id, user=user, session=session
    )
    return NoContent
