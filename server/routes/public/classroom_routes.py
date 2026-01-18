from fastapi import APIRouter, Body

from server.deps.authenticate import OptionalUserDep
from server.deps.pagination_dep import PaginationDep
from server.deps.session_dep import SessionDep
from server.deps.interval_dep import QueryInterval, QueryIntervalDep
from server.models.database.classroom_db_model import Classroom
from server.models.http.responses.classroom_response_models import (
    ClassroomResponse,
    ClassroomFullResponse,
)
from server.models.http.responses.paginated_response_models import PaginatedResponse
from server.repositories.classroom_repository import ClassroomRepository
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.classroom_permission_type_enum import ClassroomPermissionType
from server.utils.must_be_int import must_be_int

embed = Body(..., embed=True)

router = APIRouter(
    prefix="/classrooms",
    tags=["Classrooms"],
)


@router.get("")
async def get_all_classrooms(
    user: OptionalUserDep,
    session: SessionDep,
) -> list[ClassroomResponse]:
    classrooms: list[Classroom] = []
    if not user:
        classrooms = ClassroomRepository.get_all_public(session=session)

    if user and user.is_admin:
        classrooms = ClassroomRepository.get_all(session=session)

    if user and not user.is_admin:
        classrooms = ClassroomRepository.get_all_user_allowed(
            user_id=must_be_int(user.id),
            session=session,
            permission=ClassroomPermissionType.RESERVE,
            allowed_classroom_ids=user.classrooms_ids(),
        )
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
    interval: QueryIntervalDep = QueryInterval(
        start=BrazilDatetime.current_semester()[0],
        end=BrazilDatetime.current_semester()[1],
    ),
) -> list[ClassroomFullResponse]:
    """Get all classrooms with schedules and occurrences"""
    classrooms = ClassroomRepository.get_all(session=session)
    return ClassroomFullResponse.from_classroom_list(classrooms, interval=interval)
