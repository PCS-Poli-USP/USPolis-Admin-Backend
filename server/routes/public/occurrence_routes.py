from fastapi import APIRouter

from server.deps.repository_adapters.occurrence_repository_adapter import (
    OccurrenceRepositoryDep,
)
from server.models.http.responses.occurrence_response_models import OccurrenceResponse


router = APIRouter(prefix="/occurrences", tags=["Occurrences", "Public"])


@router.get("")
def get_all_occurrences(
    repository: OccurrenceRepositoryDep,
) -> list[OccurrenceResponse]:
    occurrences = repository.get_all()
    return OccurrenceResponse.from_occurrence_list(occurrences)
