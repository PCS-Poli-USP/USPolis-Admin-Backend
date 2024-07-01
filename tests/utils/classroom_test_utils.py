from datetime import datetime

from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.user_db_model import User
from server.models.http.requests.classroom_request_models import ClassroomRegister
from server.routes.restricted.classroom_routes import ClassroomInBuildingAlredyExists
from tests.utils.default_values.test_classroom_default_values import (
    ClassroomDefaultValues,
)


def make_classroom(name: str, building: Building, user: User) -> Classroom:
    classroom = Classroom(
        name=name,
        building=building, # type: ignore
        capacity=ClassroomDefaultValues.CAPACITY,
        floor=ClassroomDefaultValues.FLOOR,
        ignore_to_allocate=ClassroomDefaultValues.IGNORE_TO_ALLOCATE,
        accessibility=ClassroomDefaultValues.ACCESSIBILITY,
        projector=ClassroomDefaultValues.PROJECTOR,
        air_conditioning=ClassroomDefaultValues.AIR_CONDITIONING,
        created_by=user, # type: ignore
        updated_at=datetime.now(),
    )
    return classroom


def make_classroom_register_input(name: str, building_id: str) -> ClassroomRegister:
    register = ClassroomRegister(
        name=name,
        building_id=building_id,
        capacity=ClassroomDefaultValues.CAPACITY,
        floor=ClassroomDefaultValues.FLOOR,
        ignore_to_allocate=ClassroomDefaultValues.IGNORE_TO_ALLOCATE,
        accessibility=ClassroomDefaultValues.ACCESSIBILITY,
        projector=ClassroomDefaultValues.PROJECTOR,
        air_conditioning=ClassroomDefaultValues.AIR_CONDITIONING,
    )
    return register


async def add_classroom(name: str, building: Building, user: User) -> str:
    building_id = str(building.id)
    if await Classroom.check_classroom_name_exists(building_id, name):
        raise ClassroomInBuildingAlredyExists(name, building_id)
    classroom = make_classroom(name, building, user)
    await classroom.create()
    return str(classroom.id)
