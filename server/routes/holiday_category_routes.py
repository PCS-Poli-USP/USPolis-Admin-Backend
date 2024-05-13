
from fastapi import APIRouter, Body, Depends, HTTPException, status

from server.models.database.holiday_category_db_model import HolidayCategory
from server.models.http.requests.holiday_category_request_models import HolidayCategoryRegister, HolidayCategoryUpdate
from server.services.auth.authenticate import admin_authenticate

router = APIRouter(prefix="/holidays_categories",
                   tags=["Holiday Category"], dependencies=[Depends(admin_authenticate)])

embed = Body(..., embed=True)


@router.get("", response_model_by_alias=False)
async def get_all_holidays_categories() -> list[HolidayCategory]:
    return await HolidayCategory.find_all().to_list()


@router.get("/{holiday_category_id}", response_model_by_alias=False)
async def get_holiday_category(holiday_category_id: str) -> HolidayCategory:
    holiday_category: HolidayCategory = await HolidayCategory.by_id(holiday_category_id)
    return holiday_category


@router.post("")
async def create_holiday_category(holiday_category_input: HolidayCategoryRegister) -> str:
    category = holiday_category_input.category
    if await HolidayCategory.check_category_exists(category):
        raise HolidayCategoryAlreadyExists(category)
    holiday_category = HolidayCategory(
        category=category
    )
    await holiday_category.create()
    return str(holiday_category.id)


@router.put("/{holiday_category_id}")
async def update_holiday_category(holiday_category_id: str, holiday_category_input: HolidayCategoryUpdate) -> str:
    new_category = holiday_category_input.category
    if not await HolidayCategory.check_category_is_valid(holiday_category_id, new_category):
        raise HolidayCategoryAlreadyExists(new_category)
    holiday_category = await HolidayCategory.by_id(holiday_category_id)
    holiday_category.category = holiday_category_input.category
    await holiday_category.save()  # type: ignore
    return str(holiday_category.id)


@router.delete("/{holiday_category_id}")
async def delete_holiday_category(holiday_category_id: str) -> int:
    holiday_category = await HolidayCategory.by_id(holiday_category_id)
    response = await holiday_category.delete()  # type: ignore
    if response is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "No holiday category deleted"
        )
    return int(response.deleted_count)


class HolidayCategoryAlreadyExists(HTTPException):
    def __init__(self, category: str) -> None:
        super().__init__(status.HTTP_409_CONFLICT,
                         f"Holiday Category {category} already exists")
