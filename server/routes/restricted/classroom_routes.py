from fastapi import APIRouter, Body, Response

from server.deps.repository_adapters.classroom_repository_adapter import (
    ClassroomRepositoryDep,
)
from server.models.http.requests.classroom_request_models import ClassroomRegister
from server.models.http.responses.classroom_response_models import (
    ClassroomResponse,
    ClassroomWithSchedulesResponse,
)
from server.models.http.responses.generic_responses import NoContent

embed = Body(..., embed=True)

router = APIRouter(
    prefix="/classrooms",
    tags=["Classrooms"],
)


@router.get("")
async def get_all_classrooms(
    repository: ClassroomRepositoryDep,
) -> list[ClassroomResponse]:
    classrooms = repository.get_all()
    return ClassroomResponse.from_classroom_list(classrooms)


@router.get("/{id}")
async def get_classroom(
    id: int, repository: ClassroomRepositoryDep
) -> ClassroomResponse:
    classroom = repository.get_by_id(id)
    return ClassroomResponse.from_classroom(classroom)


@router.get("/with-schedules/{id}")
async def get_classroom_with_schedules(
    id: int, respository: ClassroomRepositoryDep
) -> ClassroomWithSchedulesResponse:
    classroom = respository.get_by_id(id)
    return ClassroomWithSchedulesResponse.from_classroom(classroom)


@router.post("")
async def create_classroom(
    classroom_in: ClassroomRegister, repository: ClassroomRepositoryDep
) -> ClassroomResponse:
    classroom = repository.create(classroom_in)
    return ClassroomResponse.from_classroom(classroom)


@router.put("/{id}")
async def update_classroom(
    id: int,
    classroom_input: ClassroomRegister,
    repository: ClassroomRepositoryDep,
) -> ClassroomResponse:
    classroom = repository.update(id, classroom_input)
    return ClassroomResponse.from_classroom(classroom)


@router.delete("/{id}")
async def delete_classroom(id: int, repository: ClassroomRepositoryDep) -> Response:
    repository.delete(id)
    return NoContent
