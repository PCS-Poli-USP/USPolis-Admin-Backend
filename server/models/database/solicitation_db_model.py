from datetime import datetime
from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship

from server.models.database.base_db_model import BaseModel
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.solicitation_status import SolicitationStatus


if TYPE_CHECKING:
    from server.models.database.user_db_model import User
    from server.models.database.building_db_model import Building
    from server.models.database.reservation_db_model import Reservation


class Solicitation(BaseModel, table=True):
    capacity: int
    required_classroom: bool = Field(default=False)
    status: SolicitationStatus = Field()
    closed_by: str | None = Field(nullable=True, default=None)
    deleted_by: str | None = Field(nullable=True, default=None)

    created_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    updated_at: datetime = Field(default_factory=BrazilDatetime.now_utc)

    user_id: int = Field(foreign_key="user.id")
    building_id: int = Field(foreign_key="building.id")
    reservation_id: int = Field(foreign_key="reservation.id")

    building: "Building" = Relationship(back_populates="solicitations")
    reservation: "Reservation" = Relationship(back_populates="solicitation")
    user: "User" = Relationship(back_populates="solicitations")

    def get_administrative_users(self) -> list["User"]:
        """
        Get the list of users who have administrative access to this solicitation. That means users who can approve, deny, or update the solicitation.

        If the solicitation is associated with a classroom, it returns the users that have access to the classroom.

        Otherwise, it returns the users that have access to the building.

        Returns:
            List of User objects.
        """
        if self.reservation.classroom is None:
            return self.building.get_users()
        return self.reservation.classroom.get_users()

    def get_administrative_users_for_email(self) -> list["User"]:
        """
        Get the list of users who have administrative access to this solicitation. That means users who can approve, deny, or update the solicitation.

        If the solicitation is associated with a classroom, it returns the users that have access to the classroom.

        Otherwise, it returns the users that have access to the building.

        Returns:
            List of User objects.
        """
        users = self.get_administrative_users()
        return [user for user in users if user.receive_emails]
