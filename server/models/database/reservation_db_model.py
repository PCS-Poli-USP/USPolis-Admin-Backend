from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Relationship, SQLModel, Field

if TYPE_CHECKING:
    from server.models.database.classroom_db_model import Classroom
    from server.models.database.schedule_db_model import Schedule
    from server.models.database.user_db_model import User


class Reservation(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    name: str
    type: str
    description: str
    updated_at: datetime

    classroom_id: int | None = Field(
        default=None, index=True, foreign_key="classroom.id", nullable=False
    )
    classroom: "Classroom" = Relationship(back_populates="reservations")

    schedule_id: int | None = Field(
        default=None, index=True, foreign_key="schedule.id", nullable=False
    )
    schedule: "Schedule" = Relationship(back_populates="reservation")

    created_by_id: int | None = Field(
        default=None, index=True, foreign_key="user.id", nullable=False
    )
    created_by: "User" = Relationship(back_populates="reservations")
