from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Body, Depends, status

from server.services.auth.authenticate import authenticate
from server.models.database.user_db_model import User
from server.models.database.classroom_db_model import Classroom
from server.models.database.building_db_model import Building
from server.models.http.requests.classroom_request_models import ClassroomRegister


embed = Body(..., embed=True)

router = APIRouter(
    prefix="/classrooms", tags=["Classrooms"], dependencies=[Depends(authenticate)]
)


@router.get("")
async def get_all_classrooms() -> list[Classroom]:
    """Get all classroom"""
    return await Classroom.find_all().to_list()


@router.get("/{classroom_id}")
async def get_classroom(classroom_id: str) -> Classroom:
    """Get a classroom"""
    return await Classroom.by_id(classroom_id)


@router.post("")
async def create_classroom(classroom_input: ClassroomRegister, user: Annotated[User, Depends(authenticate)]) -> str:
    building = await Building.by_id(classroom_input.building_id)

    building_id = classroom_input.building_id
    classroom_name = classroom_input.name
    if await Classroom.by_building_and_classroom(building_id, classroom_name):
        raise ClassroomInBuildingAlredyExists(building_id)

    classroom = Classroom(
        building=building,
        name=classroom_input.name,
        capacity=classroom_input.capacity,
        floor=classroom_input.floor,
        accessibility=classroom_input.accessibility,
        projector=classroom_input.projector,
        air_conditioning=classroom_input.air_conditioning,
        ignore_to_allocate=classroom_input.ignore_to_allocate,
        created_by=user,
        updated_at=datetime.now()
    )
    await classroom.save()
    return str(classroom.id)


@router.patch("/{classroom_id}")
async def update_classroom(classroom_id: str, classroom_input: ClassroomRegister) -> str:
    """Update a classroom, not allowing two classrooms with same name in same building"""
    building_id = classroom_input.building_id
    classroom_name = classroom_input.name
    new_classroom = await Classroom.by_building_and_classroom(building_id, classroom_name)
    if new_classroom:
        if (str(new_classroom.id) != classroom_id):
          raise ClassroomInBuildingAlredyExists(classroom_name, building_id)
    else:
        new_classroom = await Classroom.by_id(classroom_id)

    new_classroom.name = classroom_input.name
    new_classroom.capacity = classroom_input.capacity
    new_classroom.floor = classroom_input.floor
    new_classroom.ignore_to_allocate = classroom_input.ignore_to_allocate
    new_classroom.accessibility = classroom_input.accessibility
    new_classroom.projector = classroom_input.projector
    new_classroom.air_conditioning = classroom_input.air_conditioning
    new_classroom.updated_at = datetime.now()
    await new_classroom.save()
    return str(new_classroom.id)


@router.delete("/{classroom_id}")
async def delete_classroom(classroom_id: str) -> int:
    classroom = await Classroom.by_id(classroom_id)
    response = await classroom.delete()
    return int(response.deleted_count)


class ClassroomInBuildingAlredyExists(HTTPException):
    def __init__(self, classroom_info: str, building_info: str) -> None:
        super().__init__(status.HTTP_409_CONFLICT,
                         f"Classroom {classroom_info} in Building {building_info} already exists")
