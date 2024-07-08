from typing import Any

from fastapi import APIRouter, Response

from server.deps.conflict_checker import ConflictCheckerDep
from server.deps.repository_adapters.occurrence_repository_adapter import (
    OccurrenceRepositoryDep,
)
from server.models.database.class_db_model import Class
from server.models.database.schedule_db_model import Schedule
from server.models.http.requests.allocate_request_models import AllocateSchedule
from server.models.http.responses.generic_responses import NoContent

router = APIRouter(prefix="/occurrences", tags=["Occurrences"])


@router.post("/allocate-schedule")
def allocate_schedule(
    occurrence_repository: OccurrenceRepositoryDep,
    schedule_id: int,
    classroom_id: int,
) -> Schedule:
    schedule = occurrence_repository.allocate_schedule(schedule_id, classroom_id)
    return schedule


@router.post("/allocate-schedule-many")
def allocate_schedule_many(
    occurrence_repository: OccurrenceRepositoryDep,
    schedule_classroom_pairs: list[AllocateSchedule],
) -> Response:
    occurrence_repository.allocate_schedule_many(schedule_classroom_pairs)
    return NoContent


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


@router.get("/get-all-conflicting-occurrences")
def get_all_occurrences_grouped_by_classroom(
    conflict_checker: ConflictCheckerDep,
) -> Any:
    occurences = conflict_checker.conflicting_occurrences_by_classroom()
    return occurences
