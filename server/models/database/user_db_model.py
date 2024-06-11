from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from server.models.database.user_building_link import UserBuildingLink

if TYPE_CHECKING:
    from server.models.database.building_db_model import Building
    from server.models.database.calendar_db_model import Calendar
    from server.models.database.holiday_category_db_model import HolidayCategory
    from server.models.database.holiday_db_model import Holiday
    from server.models.database.reservation_db_model import Reservation


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str
    is_admin: bool
    name: str
    cognito_id: str
    updated_at: datetime = Field(default=datetime.now())

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
    holidays_categories: list["HolidayCategory"] | None = Relationship(
        back_populates="created_by"
    )
    holidays: list["Holiday"] | None = Relationship(back_populates="created_by")
    calendars: list["Calendar"] | None = Relationship(back_populates="created_by")
    reservations: list["Reservation"] | None = Relationship(back_populates="created_by")
