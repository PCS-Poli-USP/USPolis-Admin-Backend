from datetime import date
from fastapi import APIRouter

from server.deps.authenticate import OptionalUserDep
from server.deps.session_dep import SessionDep
from server.models.http.responses.allocation_response_models import (
    AllocationEventResponse,
    AllocationResourceResponse,
)
from server.repositories.building_repository import BuildingRepository
from server.repositories.occurrence_repository import OccurrenceRepository
from server.repositories.schedule_repository import ScheduleRepository
from server.utils.enums.classroom_permission_type_enum import ClassroomPermissionType


router = APIRouter(prefix="/allocations", tags=["Allocations"])


@router.get("/events")
def get_all_allocation_events(
    user: OptionalUserDep,
    session: SessionDep,
    start: date = date.today(),
    end: date = date.today(),
) -> list[AllocationEventResponse]:
    """Get all events in date interval [start, end], if not provided, it will return all events on current day"""
    occurrences = OccurrenceRepository.get_all_on_interval_for_allocation(
        start, end, session
    )
    schedules = ScheduleRepository.get_all_unallocated_for_classes(session=session)

    # Filter only public occurrences and schedules
    if user is None:
        occurrences = [
            occ
            for occ in occurrences
            if not occ.classroom or not occ.classroom.restricted
        ]
        schedules = [
            sch
            for sch in schedules
            if sch.classroom is not None and not sch.classroom.restricted
        ]

    if user is not None and not user.is_admin and not user.buildings:
        permitted_classroom_ids = user.get_permissioned_classrooms_ids_set(
            permission_type=ClassroomPermissionType.VIEW
        )
        occurrences = [
            occ
            for occ in occurrences
            if occ.classroom is None
            or not occ.classroom.restricted
            or occ.classroom.id in permitted_classroom_ids
        ]
        schedules = [
            sch
            for sch in schedules
            if sch.classroom is None
            or not sch.classroom.restricted
            or sch.classroom.id in permitted_classroom_ids
        ]
    events = AllocationEventResponse.from_occurrence_list(occurrences)
    events.extend(AllocationEventResponse.from_schedule_list(schedules))
    return events


@router.get("/resources")
def get_all_allocation_resources(
    user: OptionalUserDep,
    session: SessionDep,
) -> list[AllocationResourceResponse]:
    buildings = BuildingRepository.get_all(session=session)
    skip_restricted = False
    if user is not None and user.is_admin:
        skip_restricted = True

    allowed_classrooms_ids: set[int] = set()
    if user is not None and not user.is_admin:
        allowed_classrooms_ids.update(
            user.get_permissioned_classrooms_ids_set(ClassroomPermissionType.VIEW)
        )
    resources = AllocationResourceResponse.from_building_list(
        buildings,
        allowed_classrooms_ids,
        skip_restricted_check=skip_restricted,
    )
    resources.append(AllocationResourceResponse.unnallocated_building())
    resources.append(AllocationResourceResponse.unnallocated_classroom())
    return resources
