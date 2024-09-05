from datetime import datetime, time, date as date_type
from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

from server.utils.enums.reservation_type import ReservationType


if TYPE_CHECKING:
    from server.models.database.building_db_model import Building
    from server.models.database.classroom_db_model import Classroom


class ClassroomSolicitation(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    email: str
    classroom_id: int = Field(foreign_key="classroom.id")
    classroom: "Classroom" = Relationship(back_populates="solicitations")

    building_id: int = Field(foreign_key="building.id")
    building: "Building" = Relationship(back_populates="solicitations")

    reason: str
    reservation_type: ReservationType
    date: date_type
    start_time: time
    end_time: time
    capacity: int
    approved: bool = Field(default=False)
    denied: bool = Field(default=False)
    closed: bool = Field(default=False)
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())
