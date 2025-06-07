from fastapi import APIRouter, Body

from server.deps.repository_adapters.class_repository_adapter import (
    ClassRepositoryDep,
)
from server.models.http.responses.class_response_models import (
    ClassResponse,
    ClassFullResponse,
)

embed = Body(..., embed=True)

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.get("/{class_id}")
def get_class(class_id: int, repository: ClassRepositoryDep) -> ClassResponse:
    """Get a class by id"""
    class_ = repository.get_by_id(id=class_id)
    return ClassResponse.from_class(class_)


@router.get("/{class_id}/full")
def get_class_full(class_id: int, repository: ClassRepositoryDep) -> ClassFullResponse:
    """Get a class by id with schedules and occurrences"""
    class_ = repository.get_by_id(id=class_id)
    return ClassFullResponse.from_class(class_)
