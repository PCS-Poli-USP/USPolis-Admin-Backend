from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from server.models.database.user_building_link import UserBuildingLink

if TYPE_CHECKING:
    from server.models.database.user_db_model import User


class Building(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    created_by_id: int | None = Field(default=None, foreign_key="user.id")
    created_by: "User" = Relationship()
    users: list["User"] | None = Relationship(
        back_populates="buildings", link_model=UserBuildingLink
    )
    updated_at: datetime = Field(default=datetime.now())
