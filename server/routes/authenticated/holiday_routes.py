from fastapi import APIRouter, Body

from server.deps.session_dep import SessionDep
from server.models.http.responses.holiday_response_models import HolidayResponse
from server.repositories.holiday_repository import HolidayRepository

router = APIRouter(prefix="/holidays", tags=["Holiday"])

embed = Body(..., embed=True)


@router.get("", response_model_by_alias=False)
def get_all_holidays(session: SessionDep) -> list[HolidayResponse]:
    """Get all holidays"""
    holidays = HolidayRepository.get_all(session=session)
    return HolidayResponse.from_holiday_list(holidays)


@router.get("/{holiday_id}", response_model_by_alias=False)
def get_holiday(holiday_id: int, session: SessionDep) -> HolidayResponse:
    """Get holiday by id"""
    holiday = HolidayRepository.get_by_id(id=holiday_id, session=session)
    return HolidayResponse.from_holiday(holiday)
