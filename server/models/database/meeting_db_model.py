from sqlmodel import Field, Relationship
from server.models.database.base_db_model import BaseModel
from server.models.database.reservation_db_model import Reservation
from server.models.database.solicitation_db_model import Solicitation


class Meeting(BaseModel, table=True):
    reservation_id: int = Field(foreign_key="reservation.id", unique=True)
    link: str | None = Field(nullable=True, default=None)

    reservation: Reservation = Relationship(back_populates="meeting")

    def get_solicitation(self) -> Solicitation | None:
        """
        Get the solicitation associated with the meeting if exists.
        """
        return self.reservation.solicitation
