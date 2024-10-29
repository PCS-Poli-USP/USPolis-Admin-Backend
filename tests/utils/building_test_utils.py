from datetime import datetime

from sqlmodel import Session, select

from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User


def make_building(name: str, user: User) -> Building:
    """Make a building created by user"""
    building = Building(
        name=name,
        created_by=user,
        updated_at=datetime.now(),
    )
    return building


def add_building(session: Session, name: str, user: User) -> int:
    building = make_building(name, user)
    session.add(building)
    session.commit()
    return building.id  # type: ignore


def check_name_exists(db: Session, name: str) -> bool:
    statement = select(Building).where(Building.name == name)
    result = db.exec(statement).first()
    return result is not None
