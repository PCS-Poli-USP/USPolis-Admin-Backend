from fastapi import HTTPException, status
from sqlmodel import Session, col, select

from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User
from server.models.http.requests.building_request_models import BuildingRegister


class BuildingRepository:
    @staticmethod
    def get_all(*, session: Session) -> list[Building]:
        statement = select(Building)
        buildings = list(session.exec(statement).all())
        return buildings

    @staticmethod
    def get_by_ids(*, ids: list[str], session: Session) -> list[Building]:
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
        session.commit()
        return building


class BuildingNotFound(HTTPException):
    def __init__(self, building_info: str) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND, f"Building {building_info} not found"
        )
