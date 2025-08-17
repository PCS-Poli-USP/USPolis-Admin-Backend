from sqlmodel import Field, Relationship
from server.models.database.base_db_model import BaseModel
from server.models.database.reservation_db_model import Reservation


class Meeting(BaseModel, table=True):
    reservation_id: int = Field(foreign_key="reservation.id")
    link: str | None = Field(nullable=True, default=None)

    reservation: Reservation = Relationship(back_populates="meeting")
