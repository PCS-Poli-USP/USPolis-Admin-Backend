from fastapi import APIRouter
from fastapi.responses import JSONResponse

from server.deps.repository_adapters.occurrence_repository_adapter import (
    OccurrenceRepositoryDep,
)
from server.models.http.requests.allocation_request_models import EventUpdate
from server.repositories.building_repository import BuildingRepository
from server.repositories.occurrence_repository import OccurrenceRepository
from server.repositories.schedule_repository import ScheduleRepository
from server.utils.must_be_int import must_be_int


router = APIRouter(prefix="/allocations", tags=["Allocations"])


@router.patch("/events")
def update_event(
    input: EventUpdate,
    occurrence_repo: OccurrenceRepositoryDep,
) -> JSONResponse:
    """Update an event with the provided data"""
    if input.desalocate:
        if input.all_occurrences:
            occurrence_repo.remove_schedule_allocation(input.schedule_id)
        else:
            if input.occurrence_id:
                occurrence = OccurrenceRepository.get_by_id(
                    id=input.occurrence_id, session=occurrence_repo.session
                )
                OccurrenceRepository.remove_occurrence_allocation(
                    occurrence, occurrence_repo.session
                )
    else:
        building = BuildingRepository.get_by_name(
            name=input.building, session=occurrence_repo.session
        )
        classroom = occurrence_repo.classroom_repo.get_by_name_and_building(
            input.classroom, building
        )
        if input.all_occurrences:
            schedule = ScheduleRepository.get_by_id(
                id=input.schedule_id, session=occurrence_repo.session
            )
            schedule.start_time = input.start_time
            schedule.end_time = input.end_time
            occurrence_repo.allocate_schedule(
                input.schedule_id, must_be_int(classroom.id)
            )
        else:
            if input.occurrence_id:
                occurrence = OccurrenceRepository.get_by_id(
                    id=input.occurrence_id, session=occurrence_repo.session
                )
                occurrence.start_time = input.start_time
                occurrence.end_time = input.end_time
                OccurrenceRepository.allocate_occurrence(
                    occurrence, classroom, occurrence_repo.session
                )

    occurrence_repo.session.commit()
    return JSONResponse(content={"message": "Event updated successfully"})
