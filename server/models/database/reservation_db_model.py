from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Relationship, Field

from server.models.database.base_db_model import BaseModel
from server.utils.enums.reservation_type import ReservationType

if TYPE_CHECKING:
    from server.models.database.classroom_db_model import Classroom
    from server.models.database.schedule_db_model import Schedule
    from server.models.database.user_db_model import User
    from server.models.database.classroom_solicitation_db_model import (
        ClassroomSolicitation,
    )


class Reservation(BaseModel, table=True):
    title: str = Field()
    type: ReservationType = Field()
    reason: str | None = Field(nullable=True, default=None)
    updated_at: datetime = Field(default_factory=datetime.now)

    classroom_id: int = Field(foreign_key="classroom.id", nullable=False)
    classroom: "Classroom" = Relationship(back_populates="reservations")

    schedule: "Schedule" = Relationship(
        back_populates="reservation", sa_relationship_kwargs={"cascade": "delete"}
    )

    created_by_id: int = Field(index=True, foreign_key="user.id", nullable=False)
    created_by: "User" = Relationship(back_populates="reservations")

    solicitation: Optional["ClassroomSolicitation"] = Relationship(
        back_populates="reservation",
    )
