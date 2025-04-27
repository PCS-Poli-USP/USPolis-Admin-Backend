from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from server.models.database.group_db_model import Group
from server.models.database.group_user_link import GroupUserLink
from server.models.database.user_building_link import UserBuildingLink
from server.utils.must_be_int import must_be_int

if TYPE_CHECKING:
    from server.models.database.building_db_model import Building
    from server.models.database.calendar_db_model import Calendar
    from server.models.database.holiday_category_db_model import HolidayCategory
    from server.models.database.holiday_db_model import Holiday
    from server.models.database.reservation_db_model import Reservation
    from server.models.database.classroom_solicitation_db_model import (
        ClassroomSolicitation,
    )


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    is_admin: bool
    name: str
    updated_at: datetime = Field(default_factory=datetime.now)
    last_visited: datetime = Field(default_factory=datetime.now)

    created_by_id: int | None = Field(
        foreign_key="user.id",
        default=None,
        nullable=True,
    )
    created_by: Optional["User"] = Relationship(
        sa_relationship_kwargs=dict(remote_side="User.id"),
    )
    buildings: list["Building"] | None = Relationship(
        back_populates="users", link_model=UserBuildingLink
    )
    holidays_categories: list["HolidayCategory"] = Relationship(
        back_populates="created_by"
    )
    holidays: list["Holiday"] = Relationship(back_populates="created_by")
    calendars: list["Calendar"] = Relationship(back_populates="created_by")
    reservations: list["Reservation"] = Relationship(back_populates="created_by")
    solicitations: list["ClassroomSolicitation"] = Relationship(back_populates="user")
    groups: list[Group] = Relationship(
        link_model=GroupUserLink,
        back_populates="users",
        sa_relationship_kwargs={"order_by": "Group.name"},
    )

    def classrooms_ids_set(self) -> set[int]:
        """
        Get the set of classroom IDs that the user has access to.

        Returns:
            set[int]: A set of classroom IDs.
        """
        return {
            must_be_int(classroom.id)
            for group in self.groups
            for classroom in group.classrooms
        }

    def buildings_ids_set(self) -> set[int]:
        """
        Get the set of building IDs that the user has access to.

        Returns:
            set[int]: A set of building IDs.
        """
        if self.buildings is None:
            return set()
        return {must_be_int(building.id) for building in self.buildings}
