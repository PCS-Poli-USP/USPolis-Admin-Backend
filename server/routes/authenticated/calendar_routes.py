from datetime import date
from fastapi import APIRouter, Body

from server.deps.session_dep import SessionDep
from server.models.http.responses.calendar_response_models import CalendarResponse
from server.repositories.calendar_repository import CalendarRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/calendars", tags=["Calendars"])


@router.get("")
def get_all_calendars_from_now(session: SessionDep) -> list[CalendarResponse]:
    """Get all calendars from now, that is, the current year and the next ones"""
    calendars = CalendarRepository.get_all_from_now(session=session)
    return CalendarResponse.from_calendar_list(calendars)

@router.get("/year/{year}")
def get_all_calendars_on_year(
    session: SessionDep, year: int = date.today().year
) -> list[CalendarResponse]:
    """Get all calendars on a specific year, by default is the current year"""
    calendars = CalendarRepository.get_all_on_year(session=session, year=year)
    return CalendarResponse.from_calendar_list(calendars)


@router.get("/{calendar_id}")
def get_calendar(calendar_id: int, session: SessionDep) -> CalendarResponse:
    """Get a calendar by id"""
    calendar = CalendarRepository.get_by_id(id=calendar_id, session=session)
    return CalendarResponse.from_calendar(calendar)
