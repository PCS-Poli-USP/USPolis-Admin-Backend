from fastapi import APIRouter, Body

from server.deps.repository_adapters.subject_repository_adapter import (
    SubjectRepositoryDep,
)
from server.models.http.responses.subject_response_models import (
    SubjectResponse,
)

embed = Body(..., embed=True)

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("/{subject_id}")
def get_subject(subject_id: int, repository: SubjectRepositoryDep) -> SubjectResponse:
    """Get a subject"""
    subject = repository.get_by_id(id=subject_id)
    return SubjectResponse.from_subject(subject)
