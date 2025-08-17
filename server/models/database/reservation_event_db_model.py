from sqlmodel import Field, Relationship, Column, Enum
from server.models.database.base_db_model import BaseModel
from server.models.database.reservation_db_model import Reservation
from server.utils.enums.event_type_enum import EventType


class ReservationEvent(BaseModel, table=True):
    reservation_id: int = Field(foreign_key="reservation.id")
    link: str | None = Field(nullable=True, default=None)
    type: EventType = Field(
        sa_column=Column(
            Enum(EventType), nullable=False, server_default=EventType.OTHER.name
        )
    )

    reservation: Reservation = Relationship(back_populates="event")
