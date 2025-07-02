from datetime import datetime, time, date
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship
from sqlalchemy import CheckConstraint, Column, ARRAY, Date

from server.models.database.base_db_model import BaseModel
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.reservation_type import ReservationType
from server.utils.enums.solicitation_status import SolicitationStatus


if TYPE_CHECKING:
    from server.models.database.user_db_model import User
    from server.models.database.building_db_model import Building
    from server.models.database.classroom_db_model import Classroom
    from server.models.database.reservation_db_model import Reservation


class ClassroomSolicitation(BaseModel, table=True):
    __table_args__ = (
        CheckConstraint(
            "(classroom_id IS NOT NULL) OR (required_classroom = FALSE)",
            name="check_required_classroom_with_classroom_id_not_null",
        ),
    )

    classroom_id: int | None = Field(foreign_key="classroom.id", nullable=True)
    classroom: Optional["Classroom"] = Relationship(back_populates="solicitations")
    required_classroom: bool = Field(default=False)

    building_id: int = Field(foreign_key="building.id")
    building: "Building" = Relationship(back_populates="solicitations")

    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="solicitations")

    reservation_id: int | None = Field(foreign_key="reservation.id", nullable=True)
    reservation: Optional["Reservation"] = Relationship(back_populates="solicitation")

    reason: str | None = Field(nullable=True, default=None)
    reservation_title: str
    reservation_type: ReservationType
    dates: list[date] = Field(
        sa_column=Column(ARRAY(Date), nullable=False), min_length=1
    )
    start_time: time | None = Field(nullable=True, default=None)
    end_time: time | None = Field(nullable=True, default=None)
    capacity: int

    status: SolicitationStatus = Field()
    closed_by: str | None = Field(nullable=True, default=None)
    deleted_by: str | None = Field(nullable=True, default=None)

    created_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    updated_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
