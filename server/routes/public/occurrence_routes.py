from typing import Any

from fastapi import APIRouter, Depends

from server.deps.authenticate import building_authenticate
from server.deps.conflict_checker import ConflictCheckerDep
from server.deps.repository_adapters.occurrence_repository_adapter import (
    OccurrenceRepositoryDep,
)
from server.models.database.class_db_model import Class
from server.models.database.schedule_db_model import Schedule

router = APIRouter(
    prefix="/occurrences",
    tags=["Occurrences"],
    dependencies=[Depends(building_authenticate)],
)


@router.post("/allocate-schedule")
def allocate_schedule(
    occurrence_repository: OccurrenceRepositoryDep,
    schedule_id: int,
    classroom_id: int,
) -> Schedule:
    schedule = occurrence_repository.allocate_schedule(schedule_id, classroom_id)
    return schedule


@router.post("/allocate-class")
def allocate_class(
    occurrence_repository: OccurrenceRepositoryDep,
    class_id: int,
    classroom_id: int,
) -> Class:
    class_ = occurrence_repository.allocate_class(class_id, classroom_id)
    return class_


@router.delete("/remove-schedule-allocation")
def remove_schedule_allocation(
    occurrence_repository: OccurrenceRepositoryDep,
    schedule_id: int,
) -> Schedule:
    schedule = occurrence_repository.remove_schedule_allocation(schedule_id)
    return schedule


@router.delete("/remove-class-allocation")
def remove_class_allocation(
    occurrence_repository: OccurrenceRepositoryDep,
    class_id: int,
) -> Class:
    class_ = occurrence_repository.remove_class_allocation(class_id)
    return class_


@router.get("/get-all-occurrences-grouped-by-classroom")
def get_all_occurrences_grouped_by_classroom(
    conflict_checker: ConflictCheckerDep,
) -> Any:
    occurences = conflict_checker.conflicting_occurrences_by_classroom()
    return occurences
