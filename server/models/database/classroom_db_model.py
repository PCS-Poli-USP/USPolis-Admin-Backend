from datetime import datetime
from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from server.models.database.building_db_model import Building
    from server.models.database.user_db_model import User


class Classroom(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    name: str = Field()
    capacity: int = Field()
    floor: int = Field()
    ignore_to_allocate: bool = Field(default=False)
    accessibility: bool = Field()
    projector: bool = Field()
    air_conditioning: bool = Field()
    updated_at: datetime = Field(default=datetime.now())

    created_by_id: int | None = Field(
        foreign_key="user.id", default=None, nullable=False
    )
    created_by: "User" = Relationship(back_populates="classrooms")

    building_id: int | None = Field(
        index=True, foreign_key="building.id", default=None, nullable=False
    )
    building: "Building" = Relationship(back_populates="classrooms")
