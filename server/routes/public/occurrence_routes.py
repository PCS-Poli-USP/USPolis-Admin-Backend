from fastapi import APIRouter

from server.deps.repository_adapters.occurrence_repository_adapter import (
    OccurrenceRepositoryDep,
)
from server.deps.session_dep import SessionDep
from server.models.http.responses.occurrence_response_models import OccurrenceResponse
from server.models.http.responses.schedule_response_models import ScheduleFullResponse, ScheduleResponse
from server.repositories.schedule_repository import ScheduleRepository


router = APIRouter(prefix="/occurrences", tags=["Occurrences", "Public"])


@router.get("")
def get_all_occurrences(
    repository: OccurrenceRepositoryDep,
) -> list[OccurrenceResponse]:
    occurrences = repository.get_all()
    return OccurrenceResponse.from_occurrence_list(occurrences)


@router.get("/schedule/full/{schedule_id}")
def get_occurrences_by_schedule_full(
    schedule_id: int,
    session: SessionDep,
) -> ScheduleFullResponse:
    schedule = ScheduleRepository.get_by_id(id=schedule_id, session=session)
    return ScheduleFullResponse.from_schedule(schedule)

@router.get("/schedule/{schedule_id}")
def get_schedule_response(
    schedule_id: int,
    session: SessionDep,
) -> ScheduleResponse:
    schedule = ScheduleRepository.get_by_id(id=schedule_id, session=session)
    return ScheduleResponse.from_schedule(schedule)