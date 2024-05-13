
from fastapi import APIRouter, Body, Depends, HTTPException, status
from datetime import datetime

from server.models.database.holiday_category_db_model import HolidayCategory
from server.models.database.holiday_db_model import Holiday
from server.models.http.requests.holiday_request_models import HolidayRegister, HolidayUpdate
from server.services.auth.authenticate import admin_authenticate

router = APIRouter(prefix="/holidays",
                   tags=["Holiday"], dependencies=[Depends(admin_authenticate)])

embed = Body(..., embed=True)


@router.get("", response_model_by_alias=False)
async def get_all_holidays() -> list[Holiday]:
    return await Holiday.find_all().to_list()


@router.get("/{holiday_id}", response_model_by_alias=False)
async def get_holiday(holiday_id: str) -> Holiday:
    return await Holiday.by_id(holiday_id)  # type: ignore


@router.post("")
async def create_holiday(holiday_input: HolidayRegister) -> str:
    category_id = holiday_input.category_id
    if await Holiday.check_date_in_category_exists(category_id, holiday_input.date):
        raise HolidayInCategoryAlreadyExists(
            holiday_input.date.strftime("%D-%m-%Y"), holiday_input.category_id)
    category = await HolidayCategory.by_id(category_id)
    holiday = Holiday(
        category=category,  # type: ignore
        date=holiday_input.date,
        type=holiday_input.type,
        updated_at=datetime.now()
    )
    await holiday.create()
    return str(holiday.id)


@router.put("/{holiday_id}")
async def update_holiday(holiday_id: str, holiday_input: HolidayUpdate) -> str:
    category_id = holiday_input.category_id
    if not await Holiday.check_date_is_valid(category_id, holiday_id, holiday_input.date):
        raise HolidayInCategoryAlreadyExists(
            holiday_input.date.strftime("%D-%m-%Y"), holiday_input.category_id)
    new_holiday = await Holiday.by_id(holiday_id)
    new_holiday.date = holiday_input.date
    new_holiday.type = holiday_input.type
    new_holiday.updated_at = datetime.now()
    await new_holiday.save()  # type: ignore
    return holiday_id


@router.delete("/{holiday_id}")
async def delete_holiday(holiday_id: str) -> int:
    holiday = await Holiday.by_id(holiday_id)
    response = await holiday.delete()  # type: ignore
    if response is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "No holiday deleted")
    return int(response.deleted_count)


class HolidayInCategoryAlreadyExists(HTTPException):
    def __init__(self, holiday_info: str, category_info: str) -> None:
        super().__init__(status.HTTP_409_CONFLICT,
                         f"Holiday {holiday_info} in Category {category_info} already exists")
