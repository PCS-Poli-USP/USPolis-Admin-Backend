from datetime import date, time
from typing import Annotated
from fastapi import APIRouter, Body, Query, Response

from server.deps.conflict_checker import ConflictCheckerDep
from server.deps.repository_adapters.classroom_repository_adapter import (
    ClassroomRepositoryDep,
)
from server.deps.session_dep import SessionDep
from server.models.database.classroom_db_model import ClassroomWithConflictsIndicator
from server.models.http.requests.classroom_request_models import ClassroomRegister
from server.models.http.responses.classroom_response_models import (
    ClassroomResponse,
    ClassroomFullResponse,
)
from server.models.http.responses.generic_responses import NoContent
from server.repositories.classroom_repository import ClassroomRepository

embed = Body(..., embed=True)

router = APIRouter(
    prefix="/classrooms",
    tags=["Classrooms"],
)


@router.get("/{id}")
def get_classroom(id: int, repository: ClassroomRepositoryDep) -> ClassroomResponse:
    classroom = repository.get_by_id(id)
    return ClassroomResponse.from_classroom(classroom)


@router.get("/building/{building_id}")
def get_classrooms_by_building(
    building_id: int, repository: ClassroomRepositoryDep
) -> list[ClassroomResponse]:
    """Get all classrooms on building"""
    classrooms = repository.get_all_on_building(building_id)
    return ClassroomResponse.from_classroom_list(classrooms)


@router.get("/full/{id}")
def get_classroom_full(id: int, session: SessionDep) -> ClassroomFullResponse:
    """Get by ID a classrooms with schedules and occurrences"""
    classroom = ClassroomRepository.get_by_id(id=id, session=session)
    return ClassroomFullResponse.from_classroom(classroom)


@router.get("/with-conflict-count/{building_id}/{schedule_id}")
def get_classrooms_with_conflicts_count(
    building_id: int, schedule_id: int, conflict_checker: ConflictCheckerDep
) -> list[ClassroomWithConflictsIndicator]:
    classrooms = conflict_checker.classrooms_with_conflicts_indicator_for_schedule(
        building_id, schedule_id
    )
    return classrooms


@router.get("/with-conflict-count/{building_id}")
def get_classroom_with_conflicts_count_for_time(
    building_id: int,
    start_time: time,
    end_time: time,
    dates: Annotated[list[date], Query()],
    conflict_checker: ConflictCheckerDep,
) -> list[ClassroomWithConflictsIndicator]:
    classrooms = (
        conflict_checker.classrooms_with_conflicts_indicator_for_time_and_dates(
            building_id, start_time, end_time, dates
        )
    )
    return classrooms


@router.post("")
def create_classroom(
    classroom_in: ClassroomRegister, repository: ClassroomRepositoryDep
) -> ClassroomResponse:
    """Create a classroom"""
    classroom = repository.create(classroom_in)
    return ClassroomResponse.from_classroom(classroom)


@router.put("/{id}")
def update_classroom(
    id: int,
    classroom_input: ClassroomRegister,
    repository: ClassroomRepositoryDep,
) -> ClassroomResponse:
    classroom = repository.update(id, classroom_input)
    return ClassroomResponse.from_classroom(classroom)


@router.delete("/{id}")
def delete_classroom(id: int, repository: ClassroomRepositoryDep) -> Response:
    repository.delete(id)
    return NoContent
