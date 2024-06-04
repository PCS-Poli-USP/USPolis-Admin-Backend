from fastapi import APIRouter, Response

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.calendar_request_models import (
    CalendarRegister,
    CalendarUpdate,
)
from server.models.http.responses.calendar_response_models import CalendarResponse
from server.models.http.responses.generic_responses import NoContent
from server.repositories.calendar_repository import CalendarRepository

router = APIRouter(prefix="/calendars", tags=["Calendars"])


@router.get("")
async def get_all_calendars(session: SessionDep) -> list[CalendarResponse]:
    calendars = CalendarRepository.get_all(session=session)
    return CalendarResponse.from_calendar_list(calendars)


@router.get("/{calendar_id}")
async def get_calendar(calendar_id: int, session: SessionDep) -> CalendarResponse:
    calendar = CalendarRepository.get_by_id(id=calendar_id, session=session)
    return CalendarResponse.from_calendar(calendar)


@router.post("")
async def create_calendar(
    input: CalendarRegister, user: UserDep, session: SessionDep
) -> CalendarResponse:
    calendar = CalendarRepository.create(creator=user, input=input, session=session)
    return CalendarResponse.from_calendar(calendar)


@router.put("/{calendar_id}")
async def update_calendar(
    calendar_id: int, calendar_input: CalendarUpdate, user: UserDep, session: SessionDep
) -> CalendarResponse:
    calendar = CalendarRepository.update(
        id=calendar_id, input=calendar_input, user=user, session=session
    )
    return CalendarResponse.from_calendar(calendar)


@router.delete("/{calendar_id}")
async def delete_calendar(
    calendar_id: int, user: UserDep, session: SessionDep
) -> Response:
    CalendarRepository.delete(id=calendar_id, user=user, session=session)
    return NoContent
