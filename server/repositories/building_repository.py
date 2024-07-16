from fastapi import HTTPException, status
from sqlmodel import Session, col, select

from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User
from server.models.http.requests.building_request_models import (
    BuildingRegister,
    BuildingUpdate,
)


class BuildingRepository:
    @staticmethod
    def get_all(*, session: Session) -> list[Building]:
        statement = select(Building)
        buildings = list(session.exec(statement).all())
        return buildings

    @staticmethod
    def get_by_id(id: int, *, session: Session) -> Building:
        statement = select(Building).where(col(Building.id) == id)
        building = session.exec(statement).first()
        if building is None:
            raise BuildingNotExists(str(id))
        return building

    @staticmethod
    def get_by_ids(*, ids: list[int], session: Session) -> list[Building]:
        statement = select(Building).where(col(Building.id).in_(ids))
        buildings = list(session.exec(statement).all())
        return buildings

    @staticmethod
    def create(
        *, building_in: BuildingRegister, creator: User, session: Session
    ) -> Building:
        building = Building(
            name=building_in.name,
            created_by=creator,
        )
        session.add(building)
        return building

    @staticmethod
    def update(*, id: int, input: BuildingUpdate, session: Session) -> Building:
        building = BuildingRepository.get_by_id(id=id, session=session)
        building.name = input.name
        session.add(building)
        return building

    @staticmethod
    def delete(*, id: int, session: Session) -> None:
        building = session.get_one(Building, id)
        session.delete(building)


class BuildingNotExists(HTTPException):
    def __init__(self, building_info: str) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND, f"Building with {building_info} not exists"
        )
