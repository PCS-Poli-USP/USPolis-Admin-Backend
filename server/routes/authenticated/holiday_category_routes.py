from fastapi import APIRouter, Body

from server.deps.session_dep import SessionDep
from server.models.http.responses.holiday_category_response_models import (
    HolidayCategoryResponse,
)
from server.repositories.holiday_category_repository import HolidayCategoryRepository

router = APIRouter(prefix="/holidays_categories", tags=["Holiday Category"])

embed = Body(..., embed=True)


@router.get("", response_model_by_alias=False)
def get_all_holidays_categories(
    session: SessionDep,
) -> list[HolidayCategoryResponse]:
    """Get all holidays categories"""
    holidays_categories = HolidayCategoryRepository.get_all(session=session)
    return HolidayCategoryResponse.from_holiday_category_list(holidays_categories)


@router.get("/{holiday_category_id}", response_model_by_alias=False)
def get_holiday_category(
    holiday_category_id: int, session: SessionDep
) -> HolidayCategoryResponse:
    """Get a holiday category by id"""
    holiday_category = HolidayCategoryRepository.get_by_id(
        id=holiday_category_id, session=session
    )
    return HolidayCategoryResponse.from_holiday_category(holiday_category)
