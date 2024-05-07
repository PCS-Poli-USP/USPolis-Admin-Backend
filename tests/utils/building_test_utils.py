from datetime import datetime

from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User
from server.routes.building_routes import BuildingNameAlreadyExists
from tests.utils.default_values.test_building_default_values import (
    BuildingDefaultValues,
)
from tests.utils.user_test_utils import get_test_admin_user


def make_building(name: str, user: User) -> Building:
    """Make a building created by user"""
    building = Building(name=name, created_by=user, updated_at=datetime.now())
    return building


async def get_testing_building() -> Building:
    if await Building.check_name_exits(BuildingDefaultValues.NAME):
        return await Building.by_name(BuildingDefaultValues.NAME)
    user = await get_test_admin_user()
    building = make_building(BuildingDefaultValues.NAME, user)
    await building.create()
    return building


async def add_building(name: str, user: User) -> str:
    if await Building.check_name_exits(name):
        raise BuildingNameAlreadyExists
    building = make_building(name, user)
    await building.create()
    return str(building.id)


async def remove_building(id: str) -> None:
    building = await Building.by_id(id)
    await building.delete()
