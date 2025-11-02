from fastapi import APIRouter, Body, Response

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.holiday_request_models import (
    HolidayManyRegister,
    HolidayRegister,
    HolidayUpdate,
)
from server.models.http.responses.generic_responses import NoContent
from server.models.http.responses.holiday_response_models import HolidayResponse
from server.repositories.holiday_repository import HolidayRepository

router = APIRouter(prefix="/holidays", tags=["Holiday"])

embed = Body(..., embed=True)


@router.post("")
def create_holiday(
    holiday_input: HolidayRegister, user: UserDep, session: SessionDep
) -> HolidayResponse:
    holiday = HolidayRepository.create(
        creator=user, input=holiday_input, session=session
    )
    return HolidayResponse.from_holiday(holiday=holiday)


@router.post("/many")
def create_many_holidays(
    input: HolidayManyRegister, user: UserDep, session: SessionDep
) -> list[HolidayResponse]:
    """Create many holidays"""
    holidays = HolidayRepository.create_many(creator=user, input=input, session=session)
    return HolidayResponse.from_holiday_list(holidays)


@router.put("/{holiday_id}")
def update_holiday(
    holiday_id: int,
    holiday_input: HolidayUpdate,
    user: UserDep,
    session: SessionDep,
) -> HolidayResponse:
    """Update holiday by id"""
    updated_holiday = HolidayRepository.update(
        id=holiday_id, input=holiday_input, user=user, session=session
    )
    return HolidayResponse.from_holiday(updated_holiday)


@router.delete("/{holiday_id}")
def delete_holiday(holiday_id: int, user: UserDep, session: SessionDep) -> Response:
    HolidayRepository.delete(id=holiday_id, user=user, session=session)
    return NoContent
