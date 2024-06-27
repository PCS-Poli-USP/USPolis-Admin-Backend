from fastapi import APIRouter, Body, Depends, Response

from server.deps.authenticate import (
    building_authenticate,
)
from server.deps.repository_adapters.classroom_repository_adapter import (
    ClassroomRepositoryDep,
)
from server.models.database.classroom_db_model import Classroom
from server.models.http.requests.classroom_request_models import ClassroomRegister
from server.models.http.responses.generic_responses import NoContent

embed = Body(..., embed=True)

router = APIRouter(
    prefix="/classrooms",
    tags=["Classrooms"],
    dependencies=[Depends(building_authenticate)],
)


@router.get("", response_model_by_alias=False)
async def get_all_classrooms(
    repository: ClassroomRepositoryDep,
) -> list[Classroom]:
    return repository.get_all()


@router.get("/{id}", response_model_by_alias=False)
async def get_classroom(id: int, repository: ClassroomRepositoryDep) -> Classroom:
    return repository.get_by_id(id)


@router.post("")
async def create_classroom(
    classroom_in: ClassroomRegister, repository: ClassroomRepositoryDep
) -> int:
    classroom = repository.create(classroom_in)
    return classroom.id  # type: ignore


@router.put("/{id}")
async def update_classroom(
    id: int,
    classroom_input: ClassroomRegister,
    repository: ClassroomRepositoryDep,
) -> Classroom:
    return repository.update(id, classroom_input)


@router.delete("/{id}")
async def delete_classroom(
    id: int, repository: ClassroomRepositoryDep
) -> Response:
    repository.delete(id)
    return NoContent
