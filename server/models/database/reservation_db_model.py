from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Relationship, SQLModel, Field

from server.utils.enums.reservation_type import ReservationType

if TYPE_CHECKING:
    from server.models.database.classroom_db_model import Classroom
    from server.models.database.schedule_db_model import Schedule
    from server.models.database.user_db_model import User


class Reservation(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "name", "classroom_id", name="unique_reservation_name_for_classroom"
        ),
    )
    id: int | None = Field(primary_key=True, default=None)
    name: str = Field()
    type: ReservationType = Field()
    description: str | None = Field(nullable=True, default=None)
    updated_at: datetime = Field(default=datetime.now())

    classroom_id: int | None = Field(
        default=None, foreign_key="classroom.id", nullable=False
    )
    classroom: "Classroom" = Relationship(back_populates="reservations")

    schedule: "Schedule" = Relationship(
        back_populates="reservation", sa_relationship_kwargs={"cascade": "delete"}
    )

    created_by_id: int = Field(index=True, foreign_key="user.id", nullable=False)
    created_by: "User" = Relationship(back_populates="reservations")
