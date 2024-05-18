from fastapi import APIRouter, Body, HTTPException, status, Depends
from typing import Annotated

from server.models.database.user_db_model import User
from server.models.database.holiday_category_db_model import HolidayCategory
from server.models.http.requests.holiday_category_request_models import (
    HolidayCategoryRegister,
    HolidayCategoryUpdate,
)
from server.models.http.responses.holiday_category_response_models import HolidayCategoryResponse
from server.services.auth.authenticate import authenticate

router = APIRouter(prefix="/holidays_categories", tags=["Holiday Category"])

embed = Body(..., embed=True)


@router.get("", response_model_by_alias=False)
async def get_all_holidays_categories() -> list[HolidayCategoryResponse]:
    holidays_categories = await HolidayCategory.find_all().to_list()
    return await HolidayCategoryResponse.from_holiday_category_list(holidays_categories)


@router.get("/{holiday_category_id}", response_model_by_alias=False)
async def get_holiday_category(holiday_category_id: str) -> HolidayCategoryResponse:
    holiday_category: HolidayCategory = await HolidayCategory.by_id(holiday_category_id)
    return await HolidayCategoryResponse.from_holiday_category(holiday_category)


@router.post("")
async def create_holiday_category(
    holiday_category_input: HolidayCategoryRegister, user: Annotated[User, Depends(authenticate)]
) -> str:
    name = holiday_category_input.name
    if await HolidayCategory.check_name_exists(name):
        raise HolidayCategoryAlreadyExists(name)
    holiday_category = HolidayCategory(
        name=name, created_by=user)  # type: ignore
    await holiday_category.create()
    return str(holiday_category.id)


@router.put("/{holiday_category_id}")
async def update_holiday_category(
    holiday_category_id: str, holiday_category_input: HolidayCategoryUpdate
) -> str:
    new_name = holiday_category_input.name
    if not await HolidayCategory.check_category_is_valid(
        holiday_category_id, new_name
    ):
        raise HolidayCategoryAlreadyExists(new_name)
    holiday_category = await HolidayCategory.by_id(holiday_category_id)
    holiday_category.name = holiday_category_input.name
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
        super().__init__(
            status.HTTP_409_CONFLICT, f"Holiday Category {category} already exists"
        )
