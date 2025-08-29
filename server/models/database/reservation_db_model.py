from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Relationship, Field, Column, Enum

from server.exceptions.database_exceptions import DatabaseInconsistencyException
from server.models.database.base_db_model import BaseModel
from server.models.database.building_db_model import Building
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.audiovisual_type_enum import AudiovisualType
from server.utils.enums.reservation_type import ReservationType

if TYPE_CHECKING:
    from server.models.database.classroom_db_model import Classroom
    from server.models.database.schedule_db_model import Schedule
    from server.models.database.user_db_model import User
    from server.models.database.solicitation_db_model import (
        Solicitation,
    )
    from server.models.database.exam_db_model import Exam
    from server.models.database.meeting_db_model import Meeting
    from server.models.database.event_db_model import Event


class Reservation(BaseModel, table=True):
    title: str = Field()
    type: ReservationType = Field()
    reason: str | None = Field(nullable=True, default=None)
    updated_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    audiovisual: AudiovisualType = Field(
        default_factory=lambda: AudiovisualType.NONE,
        sa_column=Column(
            Enum(AudiovisualType),
            nullable=False,
            server_default=AudiovisualType.NONE.name,
        ),
    )
    created_by_id: int = Field(index=True, foreign_key="user.id", nullable=False)

    schedule: "Schedule" = Relationship(
        back_populates="reservation", sa_relationship_kwargs={"cascade": "delete"}
    )
    created_by: "User" = Relationship(back_populates="reservations")
    solicitation: Optional["Solicitation"] = Relationship(
        back_populates="reservation", sa_relationship_kwargs={"cascade": "delete"}
    )
    exam: Optional["Exam"] = Relationship(
        back_populates="reservation", sa_relationship_kwargs={"cascade": "delete"}
    )
    event: Optional["Event"] = Relationship(
        back_populates="reservation", sa_relationship_kwargs={"cascade": "delete"}
    )
    meeting: Optional["Meeting"] = Relationship(
        back_populates="reservation", sa_relationship_kwargs={"cascade": "delete"}
    )

    def get_classroom(self) -> Optional["Classroom"]:
        """Get the classroom associated with this reservation, if any.

        Returns:
            The classroom associated with this reservation, or None if there is no classroom.
        """
        return self.schedule.classroom

    def get_building(self) -> Building:
        """Get the building associated with this reservation.

        Returns:
            The building associated with this reservation.
        """
        classroom = self.get_classroom()
        if not classroom:
            solicitation = self.solicitation
            if not solicitation:
                raise DatabaseInconsistencyException(
                    f"A reserva {self.title} não está associada a uma sala de aula ou solicitação."
                )
            return solicitation.building
        return classroom.building
