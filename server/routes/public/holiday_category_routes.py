from fastapi import APIRouter, Body, Response

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.holiday_category_request_models import (
    HolidayCategoryRegister,
    HolidayCategoryUpdate,
)
from server.models.http.responses.generic_responses import NoContent
from server.models.http.responses.holiday_category_response_models import (
    HolidayCategoryResponse,
)
from server.repositories.holiday_category_repository import HolidayCategoryRepository

router = APIRouter(prefix="/holidays_categories", tags=["Holiday Category"])

embed = Body(..., embed=True)


@router.get("", response_model_by_alias=False)
async def get_all_holidays_categories(
    session: SessionDep,
) -> list[HolidayCategoryResponse]:
    holidays_categories = HolidayCategoryRepository.get_all(session=session)
    return HolidayCategoryResponse.from_holiday_category_list(holidays_categories)


@router.get("/{holiday_category_id}", response_model_by_alias=False)
async def get_holiday_category(
    holiday_category_id: int, session: SessionDep
) -> HolidayCategoryResponse:
    holiday_category = HolidayCategoryRepository.get_by_id(
        id=holiday_category_id, session=session
    )
    return HolidayCategoryResponse.from_holiday_category(holiday_category)


@router.post("")
async def create_holiday_category(
    holiday_category_input: HolidayCategoryRegister, user: UserDep, session: SessionDep
) -> HolidayCategoryResponse:
    new_holiday_category = HolidayCategoryRepository.create(
        creator=user, input=holiday_category_input, session=session
    )
    return HolidayCategoryResponse.from_holiday_category(new_holiday_category)


@router.put("/{holiday_category_id}")
async def update_holiday_category(
    holiday_category_id: int,
    holiday_category_input: HolidayCategoryUpdate,
    user: UserDep,
    session: SessionDep,
) -> HolidayCategoryResponse:
    updated = HolidayCategoryRepository.update(
        id=holiday_category_id, input=holiday_category_input, user=user, session=session
    )
    return HolidayCategoryResponse.from_holiday_category(updated)


@router.delete("/{holiday_category_id}")
async def delete_holiday_category(
    holiday_category_id: int, user: UserDep, session: SessionDep
) -> Response:
    HolidayCategoryRepository.delete(id=holiday_category_id, user=user, session=session)
    return NoContent
