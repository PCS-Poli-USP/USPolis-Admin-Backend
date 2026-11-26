from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import CheckConstraint
from sqlmodel import Field, Relationship

from server.models.database.base_db_model import BaseModel
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.reservation_status import ReservationStatus


if TYPE_CHECKING:
    from server.models.database.user_db_model import User
    from server.models.database.building_db_model import Building
    from server.models.database.classroom_db_model import Classroom
    from server.models.database.reservation_db_model import Reservation


class Solicitation(BaseModel, table=True):
    __table_args__ = (
        CheckConstraint(
            "(solicited_classroom_id IS NOT NULL) OR (required_classroom = FALSE)",
            name="check_required_classroom_with_solicited_classroom_id_not_null",
        ),
    )

    capacity: int
    required_classroom: bool = Field(default=False)
    closed_by: str | None = Field(nullable=True, default=None)
    deleted_by: str | None = Field(nullable=True, default=None)

    created_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    updated_at: datetime = Field(default_factory=BrazilDatetime.now_utc)

    solicited_classroom_id: int | None = Field(foreign_key="classroom.id", default=None)
    building_id: int = Field(foreign_key="building.id")
    reservation_id: int = Field(foreign_key="reservation.id")
    user_id: int = Field(foreign_key="user.id")

    building: "Building" = Relationship(back_populates="solicitations")
    solicited_classroom: Optional["Classroom"] = Relationship(
        back_populates="solicitations"
    )
    reservation: "Reservation" = Relationship(back_populates="solicitation")
    user: "User" = Relationship(back_populates="solicitations")

    def get_status(self) -> ReservationStatus:
        """
        Get the status of the reservation associated with this solicitation.

        Returns:
            ReservationStatus: The status of the reservation.
        """
        return self.reservation.status

    def set_status(self, status: ReservationStatus) -> None:
        """
        Set the status of the reservation associated with this solicitation.

        Args:
            status (ReservationStatus): The new status to set.
        """
        self.reservation.status = status

    def get_responsible_classroom(self) -> Optional["Classroom"]:
        """
        The classroom whose groups handle this solicitation: the allocated
        one, or, while it is pending (nothing allocated yet), the solicited
        one. None when no classroom was chosen.
        """
        return self.reservation.get_classroom() or self.solicited_classroom

    def get_administrative_users(self) -> list["User"]:
        """
        Get the list of users who have administrative access to this solicitation. That means users who can approve, deny, or update the solicitation.

        If the solicitation has a classroom (allocated or solicited, see
        get_responsible_classroom), it returns the users that have access to
        that classroom, which includes the building main group.

        Otherwise, it returns only the users of the building main group: a
        group restricted to some classrooms must not handle solicitations
        for the whole building.

        Returns:
            List of User objects.
        """
        classroom = self.get_responsible_classroom()
        if classroom is not None:
            return classroom.get_users()
        main_group = self.building.main_group
        if main_group is None:
            return []
        return list(main_group.users)

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
