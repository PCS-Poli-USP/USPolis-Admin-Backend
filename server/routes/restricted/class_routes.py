from typing import Annotated
from fastapi import APIRouter, Body, Query, Response

from server.deps.repository_adapters.class_repository_adapter import (
    ClassRepositoryAdapterDep,
)
from server.models.http.requests.class_request_models import ClassRegister, ClassUpdate
from server.models.http.responses.class_response_models import (
    ClassResponse,
    ClassFullResponse,
)
from server.models.http.responses.generic_responses import NoContent

embed = Body(..., embed=True)

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.get("")
async def get_all_classes(repository: ClassRepositoryAdapterDep) -> list[ClassResponse]:
    """Get all classes"""
    classes = repository.get_all()
    return ClassResponse.from_class_list(classes)


@router.get("/full/")
async def get_all_classes_full(
    repository: ClassRepositoryAdapterDep,
) -> list[ClassFullResponse]:
    """Get all classes with schedules and occurrences"""
    classes = repository.get_all()
    return ClassFullResponse.from_class_list(classes)


@router.get("/{class_id}")
async def get_class(
    class_id: int, repository: ClassRepositoryAdapterDep
) -> ClassResponse:
    """Get a class by id"""
    class_ = repository.get_by_id(id=class_id)
    return ClassResponse.from_class(class_)


@router.get("/{class_id}/full")
async def get_class_full(
    class_id: int, repository: ClassRepositoryAdapterDep
) -> ClassFullResponse:
    """Get a class by id with schedules and occurrences"""
    class_ = repository.get_by_id(id=class_id)
    return ClassFullResponse.from_class(class_)


@router.post("")
async def create_class(
    class_input: ClassRegister, repository: ClassRepositoryAdapterDep
) -> ClassResponse:
    """Create a class"""
    class_ = repository.create(input=class_input)
    return ClassResponse.from_class(class_)


@router.put("/{class_id}")
async def update_class(
    class_id: int, class_input: ClassUpdate, repository: ClassRepositoryAdapterDep
) -> ClassResponse:
    """Update a class by id"""
    updated_class = repository.update(id=class_id, input=class_input)
    return ClassResponse.from_class(updated_class)


@router.delete("/{class_id}")
async def delete_class(
    class_id: int, repository: ClassRepositoryAdapterDep
) -> Response:
    """Delete a class by id"""
    repository.delete(id=class_id)
    return NoContent


@router.delete("/many/")
async def delete_many_class(
    repository: ClassRepositoryAdapterDep, ids: Annotated[list[int], Query()] = []
) -> Response:
    """Delete many classes by ids"""
    repository.delete_many(ids=ids)
    return NoContent
