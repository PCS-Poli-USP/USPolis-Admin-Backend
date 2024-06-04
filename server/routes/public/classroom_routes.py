from datetime import datetime

from fastapi import APIRouter, Body, Depends, HTTPException, status

from server.deps.authenticate import (
    BuildingDep,
    UserDep,
    building_authenticate,
)
from server.deps.session_dep import SessionDep
from server.models.database.classroom_db_model import Classroom
from server.models.http.requests.classroom_request_models import ClassroomRegister
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
    classroom = ClassroomRepository.create(
        classroom_in, building=building, creator=user, session=session
    )
    return classroom.id  # type: ignore


@router.put("/{classroom_id}")
async def update_classroom(
    classroom_id: str, classroom_input: ClassroomRegister
) -> str:
    """Update a classroom, not allowing two classrooms with same name in same building"""
    building_id = classroom_input.building_id
    classroom_name = classroom_input.name
    if not await Classroom.check_classroom_name_is_valid(
        building_id, classroom_id, classroom_name
    ):
        raise ClassroomInBuildingAlredyExists(classroom_name, building_id)

    new_classroom = await Classroom.by_id(classroom_id)
    new_classroom.name = classroom_input.name
    new_classroom.capacity = classroom_input.capacity
    new_classroom.floor = classroom_input.floor
    new_classroom.ignore_to_allocate = classroom_input.ignore_to_allocate
    new_classroom.accessibility = classroom_input.accessibility
    new_classroom.projector = classroom_input.projector
    new_classroom.air_conditioning = classroom_input.air_conditioning
    new_classroom.updated_at = datetime.now()
    await new_classroom.save()  # type: ignore
    return str(new_classroom.id)


@router.delete("/{classroom_id}")
async def delete_classroom(classroom_id: str) -> int:
    classroom = await Classroom.by_id(classroom_id)
    response = await classroom.delete()  # type: ignore
    if response is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "No classroom deleted"
        )
    return int(response.deleted_count)


class ClassroomInBuildingAlredyExists(HTTPException):
    def __init__(self, classroom_info: str, building_info: str) -> None:
        super().__init__(
            status.HTTP_409_CONFLICT,
            f"Classroom {classroom_info} in Building {building_info} already exists",
        )
