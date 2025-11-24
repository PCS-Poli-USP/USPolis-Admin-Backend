from fastapi import APIRouter, Body, Query

from server.deps.interval_dep import QueryIntervalDep
from server.deps.repository_adapters.class_repository_adapter import (
    ClassRepositoryDep,
)
from server.deps.session_dep import SessionDep
from server.models.http.responses.class_response_models import (
    ClassResponse,
    ClassFullResponse,
)
from server.repositories.class_repository import ClassRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.get("/subjects")
def get_classes_allocated_by_subjects(
    session: SessionDep,
    interval: QueryIntervalDep,
    subject_ids: list[int] = Query(...),
) -> list[ClassResponse]:
    """Get classes by subject ids"""
    classes = ClassRepository.get_all_allocated_by_subjects(
        subject_ids=subject_ids, session=session, interval=interval
    )
    return ClassResponse.from_class_list(classes)


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
