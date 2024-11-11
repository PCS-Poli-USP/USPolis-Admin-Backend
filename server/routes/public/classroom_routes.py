from fastapi import APIRouter, Body

from server.deps.session_dep import SessionDep
from server.models.http.responses.classroom_response_models import (
    ClassroomResponse,
    ClassroomFullResponse,
)
from server.repositories.classroom_repository import ClassroomRepository

embed = Body(..., embed=True)

router = APIRouter(
    prefix="/classrooms",
    tags=["Public", "Classrooms"],
)


@router.get("")
async def get_all_classrooms(
    session: SessionDep,
) -> list[ClassroomResponse]:
    classrooms = ClassroomRepository.get_all(session=session)
    return ClassroomResponse.from_classroom_list(classrooms)


@router.get("/full/")
async def get_all_classrooms_full(
    session: SessionDep,
) -> list[ClassroomFullResponse]:
    """Get all classrooms with schedules and occurrences"""
    classrooms = ClassroomRepository.get_all(session=session)
    return ClassroomFullResponse.from_classroom_list(classrooms)
