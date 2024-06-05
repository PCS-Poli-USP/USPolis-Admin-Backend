from fastapi import APIRouter, Body, Response

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.database.holiday_db_model import Holiday
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


@router.get("", response_model_by_alias=False)
async def get_all_holidays(session: SessionDep) -> list[HolidayResponse]:
    holidays = HolidayRepository.get_all(session=session)
    return HolidayResponse.from_holiday_list(holidays)


@router.get("/{holiday_id}", response_model_by_alias=False)
async def get_holiday(holiday_id: str) -> HolidayResponse:
    holiday = await Holiday.by_id(holiday_id)  # type: ignore
    return HolidayResponse.from_holiday(holiday)


@router.post("")
async def create_holiday(
    holiday_input: HolidayRegister, user: UserDep, session: SessionDep
) -> HolidayResponse:
    holiday = HolidayRepository.create(
        creator=user, input=holiday_input, session=session
    )
    return HolidayResponse.from_holiday(holiday=holiday)


@router.post("/many")
async def create_many_holidays(
    input: HolidayManyRegister, user: UserDep, session: SessionDep
) -> list[HolidayResponse]:
    holidays = HolidayRepository.create_many(creator=user, input=input, session=session)
    return HolidayResponse.from_holiday_list(holidays)


@router.put("/{holiday_id}")
async def update_holiday(
    holiday_id: int,
    holiday_input: HolidayUpdate,
    user: UserDep,
    session: SessionDep,
) -> HolidayResponse:
    updated_holiday = HolidayRepository.update(
        id=holiday_id, input=holiday_input, user=user, session=session
    )
    return HolidayResponse.from_holiday(updated_holiday)


@router.delete("/{holiday_id}")
async def delete_holiday(
    holiday_id: int, user: UserDep, session: SessionDep
) -> Response:
    HolidayRepository.delete(id=holiday_id, user=user, session=session)
    return NoContent
