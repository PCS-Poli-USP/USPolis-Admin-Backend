from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from server.deps.repository_adapters.occurrence_repository_adapter import (
    OccurrenceRepositoryDep,
)
from server.deps.session_dep import SessionDep
from server.models.http.requests.allocation_request_models import (
    AllocationReuseInput,
    EventUpdate,
)
from server.models.http.responses.allocation_response_models import (
    AllocationClassOptions,
    AllocationReuseResponse,
    AllocationReuseTargetOptions,
    AllocationScheduleOptions,
)
from server.models.http.responses.schedule_response_models import ScheduleResponseBase
from server.repositories.building_repository import BuildingRepository
from server.repositories.class_repository import ClassRepository
from server.repositories.occurrence_repository import OccurrenceRepository
from server.repositories.schedule_repository import ScheduleRepository
from server.repositories.subject_repository import SubjectRepository
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
    return JSONResponse(content={"message": "Evento atualizado com sucesso!"})


@router.post("/reuse-options")
def allocation_reuse_options(
    input: AllocationReuseInput,
    session: SessionDep,
) -> AllocationReuseResponse:
    target_options: list[AllocationReuseTargetOptions] = []
    for target in input.targets:
        subject = SubjectRepository.get_by_id(id=target.subject_id, session=session)
        classes = ClassRepository.get_by_ids(ids=target.class_ids, session=session)
        class_options: list[AllocationClassOptions] = []
        for cls in classes:
            if cls.subject_id != target.subject_id:
                raise InvalidAllocationReuseInputError(
                    "A classe não pertence à disciplina especificada."
                )

            schedule_options: list[AllocationScheduleOptions] = []
            for schedule in cls.schedules:
                options = ScheduleRepository.find_old_allocation_options(
                    building_id=input.building_id,
                    year=input.allocation_year,
                    target=schedule,
                    session=session,
                )
                schedule_options.append(
                    AllocationScheduleOptions(
                        schedule_target_id=must_be_int(schedule.id),
                        options=ScheduleResponseBase.from_schedule_list(options),
                    )
                )
            class_options.append(
                AllocationClassOptions(
                    class_id=must_be_int(cls.id),
                    class_code=cls.code,
                    schedule_options=schedule_options,
                )
            )
        target_options.append(
            AllocationReuseTargetOptions(
                subject_id=target.subject_id,
                subject_name=subject.name,
                subject_code=subject.code,
                class_options=class_options,
            )
        )

    return AllocationReuseResponse(
        building_id=input.building_id,
        allocation_year=input.allocation_year,
        target_options=target_options,
        strict=input.strict,
    )


class InvalidAllocationReuseInputError(HTTPException):
    """Custom exception for invalid allocation reuse input."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(status.HTTP_400_BAD_REQUEST, detail=message)
