from typing import Annotated
from fastapi import APIRouter, Body, Query, Response

from server.deps.repository_adapters.class_repository_adapter import (
    ClassRepositoryDep,
)
from server.models.http.requests.class_request_models import ClassRegister, ClassUpdate
from server.models.http.responses.class_response_models import (
    ClassResponse,
    ClassFullResponse,
)
from server.models.http.responses.generic_responses import NoContent

embed = Body(..., embed=True)

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.get("/{class_id}")
def get_class(class_id: int, repository: ClassRepositoryDep) -> ClassResponse:
    """Get a class by id"""
    class_ = repository.get_by_id(id=class_id)
    return ClassResponse.from_class(class_)


@router.get("/{class_id}/full")
def get_class_full(
    class_id: int, repository: ClassRepositoryDep
) -> ClassFullResponse:
    """Get a class by id with schedules and occurrences"""
    class_ = repository.get_by_id(id=class_id)
    return ClassFullResponse.from_class(class_)


@router.post("")
async def create_class(
    class_input: ClassRegister, repository: ClassRepositoryDep
) -> ClassResponse:
    """Create a class"""
    class_ = repository.create(input=class_input)
    return ClassResponse.from_class(class_)


@router.put("/{class_id}")
def update_class(
    class_id: int, class_input: ClassUpdate, repository: ClassRepositoryDep
) -> ClassResponse:
    """Update a class by id"""
    updated_class = repository.update(id=class_id, input=class_input)
    return ClassResponse.from_class(updated_class)


@router.delete("/{class_id}")
def delete_class(class_id: int, repository: ClassRepositoryDep) -> Response:
    """Delete a class by id"""
    repository.delete(id=class_id)
    return NoContent


@router.delete("/many/")
def delete_many_class(
    repository: ClassRepositoryDep, ids: Annotated[list[int], Query()] = []
) -> Response:
    """Delete many classes by ids"""
    repository.delete_many(ids=ids)
    return NoContent
