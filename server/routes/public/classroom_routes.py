from datetime import datetime

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status

from server.deps.authenticate import (
    BuildingDep,
    UserDep,
    building_authenticate,
)
from server.deps.session_dep import SessionDep
from server.models.database.classroom_db_model import Classroom
from server.models.http.requests.classroom_request_models import ClassroomRegister
from server.models.http.responses.generic_responses import NoContent
from server.repositories.classrooms_repository import ClassroomRepository

embed = Body(..., embed=True)

router = APIRouter(
    prefix="/classrooms/{building_id}",
    tags=["Classrooms"],
    dependencies=[Depends(building_authenticate)],
)


@router.get("", response_model_by_alias=False)
async def get_all_classrooms(
    building: BuildingDep, session: SessionDep
) -> list[Classroom]:
    """Get all classroom"""
    return ClassroomRepository.get_all_on_building(building=building, session=session)


@router.get("/{classroom_id}", response_model_by_alias=False)
async def get_classroom(
    classroom_id: int, building: BuildingDep, session: SessionDep
) -> Classroom:
    """Get a classroom"""
    return ClassroomRepository.get_by_id_on_building(
        classroom_id, building=building, session=session
    )


@router.post("")
async def create_classroom(
    classroom_in: ClassroomRegister,
    building: BuildingDep,
    user: UserDep,
    session: SessionDep,
) -> int:
    """Create a classroom"""
    classroom = ClassroomRepository.create(
        classroom_in, building=building, creator=user, session=session
    )
    return classroom.id  # type: ignore


@router.put("/{classroom_id}")
async def update_classroom(
    classroom_id: int,
    classroom_input: ClassroomRegister,
    building: BuildingDep,
    session: SessionDep,
) -> Classroom:
    """Update a classroom"""

    classroom = ClassroomRepository.get_by_id_on_building(
        classroom_id=classroom_id, building=building, session=session
    )
    classroom.name = classroom_input.name
    classroom.capacity = classroom_input.capacity
    classroom.floor = classroom_input.floor
    classroom.ignore_to_allocate = classroom_input.ignore_to_allocate
    classroom.accessibility = classroom_input.accessibility
    classroom.projector = classroom_input.projector
    classroom.air_conditioning = classroom_input.air_conditioning
    classroom.updated_at = datetime.now()
    session.add(classroom)
    session.commit()
    session.refresh(classroom)
    return classroom


@router.delete("/{classroom_id}")
async def delete_classroom(
    classroom_id: int, building: BuildingDep, session: SessionDep
) -> Response:
    classroom = ClassroomRepository.get_by_id_on_building(
        classroom_id=classroom_id, building=building, session=session
    )
    """Delete a classroom"""
    session.delete(classroom)
    session.commit()
    return NoContent


class ClassroomInBuildingAlredyExists(HTTPException):
    def __init__(self, classroom_info: str, building_info: str) -> None:
        super().__init__(
            status.HTTP_409_CONFLICT,
            f"Classroom {classroom_info} in Building {building_info} already exists",
        )
