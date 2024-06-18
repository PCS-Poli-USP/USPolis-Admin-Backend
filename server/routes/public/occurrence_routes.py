from fastapi import APIRouter, Depends

from server.deps.authenticate import building_authenticate
from server.deps.repository_adapters.occurrences_repository_adapter import (
    OccurrencesRepositoryDep,
)
from server.models.database.schedule_db_model import Schedule

router = APIRouter(
    prefix="/occurrences",
    tags=["Occurrences"],
    dependencies=[Depends(building_authenticate)],
)


@router.post("/allocate-schedule")
def allocate_schedule(
    occurrence_repository: OccurrencesRepositoryDep,
    schedule_id: int,
    classroom_id: int,
) -> Schedule:
    schedule = occurrence_repository.allocate_schedule(schedule_id, classroom_id)
    return schedule
