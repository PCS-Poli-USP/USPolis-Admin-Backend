from fastapi import APIRouter, Body, Response

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.calendar_request_models import (
    CalendarRegister,
    CalendarUpdate,
)
from server.models.http.responses.calendar_response_models import CalendarResponse
from server.models.http.responses.generic_responses import NoContent
from server.repositories.calendar_repository import CalendarRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/calendars", tags=["Calendars"])


@router.post("")
def create_calendar(
    input: CalendarRegister, user: UserDep, session: SessionDep
) -> CalendarResponse:
    """Create a calendar"""
    calendar = CalendarRepository.create(creator=user, input=input, session=session)
    return CalendarResponse.from_calendar(calendar)


@router.put("/{calendar_id}")
def update_calendar(
    calendar_id: int, calendar_input: CalendarUpdate, user: UserDep, session: SessionDep
) -> CalendarResponse:
    """Update a calendar by id"""
    calendar = CalendarRepository.update(
        id=calendar_id, input=calendar_input, user=user, session=session
    )
    return CalendarResponse.from_calendar(calendar)


@router.delete("/{calendar_id}")
def delete_calendar(calendar_id: int, user: UserDep, session: SessionDep) -> Response:
    """Delete a calendar by id"""
    CalendarRepository.delete(id=calendar_id, user=user, session=session)
    return NoContent
