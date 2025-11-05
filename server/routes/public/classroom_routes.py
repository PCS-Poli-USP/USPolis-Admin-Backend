from fastapi import APIRouter, Body

from server.deps.pagination_dep import PaginationDep
from server.deps.session_dep import SessionDep
from server.deps.interval_dep import QueryIntervalDep
from server.models.http.responses.classroom_response_models import (
    ClassroomResponse,
    ClassroomFullResponse,
)
from server.models.http.responses.paginated_response_models import PaginatedResponse
from server.repositories.classroom_repository import ClassroomRepository

embed = Body(..., embed=True)

router = APIRouter(
    prefix="/classrooms",
    tags=["Classrooms"],
)


@router.get("")
async def get_all_classrooms(
    session: SessionDep,
) -> list[ClassroomResponse]:
    classrooms = ClassroomRepository.get_all(session=session)
    return ClassroomResponse.from_classroom_list(classrooms)


@router.get("/paginated/")
async def get_all_classrooms_paginated(
    pagination: PaginationDep,
    session: SessionDep,
) -> PaginatedResponse[ClassroomResponse]:
    page = ClassroomRepository.get_all_paginated(pagination=pagination, session=session)
    response = PaginatedResponse[ClassroomResponse](
        page=page.page,
        page_size=page.page_size,
        total_items=page.total_items,
        total_pages=page.total_pages,
        data=ClassroomResponse.from_classroom_list(page.items),
    )
    return response


@router.get("/full/")
async def get_all_classrooms_full(
    session: SessionDep,
    interval: QueryIntervalDep,
) -> list[ClassroomFullResponse]:
    """Get all classrooms with schedules and occurrences"""
    classrooms = ClassroomRepository.get_all(session=session)
    return ClassroomFullResponse.from_classroom_list(classrooms)
