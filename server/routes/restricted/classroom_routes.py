from fastapi import APIRouter, Body, Response

from server.deps.repository_adapters.classroom_repository_adapter import (
    ClassroomRepositoryDep,
)
from server.models.http.requests.classroom_request_models import (
    ClassroomRegister,
    ClassroomUpdate,
)
from server.models.http.responses.classroom_response_models import (
    ClassroomResponse,
)
from server.models.http.responses.generic_responses import NoContent

embed = Body(..., embed=True)

router = APIRouter(
    prefix="/classrooms",
    tags=["Classrooms"],
)


@router.post("")
def create_classroom(
    input: ClassroomRegister, repository: ClassroomRepositoryDep
) -> ClassroomResponse:
    """Create a classroom"""
    classroom = repository.create(input)
    return ClassroomResponse.from_classroom(classroom)


@router.put("/{id}")
def update_classroom(
    id: int,
    input: ClassroomUpdate,
    repository: ClassroomRepositoryDep,
) -> ClassroomResponse:
    classroom = repository.update(id, input)
    return ClassroomResponse.from_classroom(classroom)


@router.delete("/{id}")
def delete_classroom(id: int, repository: ClassroomRepositoryDep) -> Response:
    repository.delete(id)
    return NoContent
