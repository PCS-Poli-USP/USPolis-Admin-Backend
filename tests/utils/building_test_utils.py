from datetime import datetime

from sqlmodel import Session, select

from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User
from tests.utils.default_values.test_building_default_values import (
    BuildingDefaultValues,
)
from tests.utils.user_test_utils import get_test_admin_user


def make_building(name: str, user: User) -> Building:
    """Make a building created by user"""
    building = Building(
        name=name,
        created_by=user,
        updated_at=datetime.now(),
    )
    return building


async def get_testing_building() -> Building:
    if await Building.check_name_exits(BuildingDefaultValues.NAME):
        building: Building = await Building.by_name(BuildingDefaultValues.NAME)
        return building
    user = await get_test_admin_user()
    building = make_building(BuildingDefaultValues.NAME, user)
    await building.create()
    return building


def add_building(session: Session, name: str, user: User) -> int:
    building = make_building(name, user)
    session.add(building)
    session.commit()
    return building.id # type: ignore


def check_name_exists(db: Session, name: str) -> bool:
    statement = select(Building).where(Building.name == name)
    result = db.exec(statement).first()
    return result is not None


async def remove_building(id: str) -> None:
    building = await Building.by_id(id)
    await building.delete()  # type: ignore
