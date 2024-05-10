from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status

from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.user_db_model import User
from server.models.http.requests.classroom_request_models import ClassroomRegister
from server.services.auth.authenticate import authenticate

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
    return await Classroom.by_id(classroom_id)  # type: ignore


@router.post("")
async def create_classroom(
    classroom_input: ClassroomRegister, user: Annotated[User, Depends(authenticate)]
) -> str:
    building = await Building.by_id(classroom_input.building_id)

    building_id = classroom_input.building_id
    classroom_name = classroom_input.name
    if await Classroom.check_classroom_name_exists(building_id, classroom_name):
        raise ClassroomInBuildingAlredyExists(classroom_name, building_id)

    classroom = Classroom(
        building=building,  # type: ignore
        name=classroom_input.name,
        capacity=classroom_input.capacity,
        floor=classroom_input.floor,
        accessibility=classroom_input.accessibility,
        projector=classroom_input.projector,
        air_conditioning=classroom_input.air_conditioning,
        ignore_to_allocate=classroom_input.ignore_to_allocate,
        created_by=user,  # type: ignore
        updated_at=datetime.now(),
    )
    await classroom.save()  # type: ignore
    await classroom.save()  # type: ignore
    return str(classroom.id)


@router.patch("/{classroom_id}")
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
