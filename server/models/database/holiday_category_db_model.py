from typing import TYPE_CHECKING
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from server.models.database.base_db_model import BaseModel
from server.models.database.calendar_holiday_category_link import (
    CalendarHolidayCategoryLink,
)


if TYPE_CHECKING:
    from server.models.database.user_db_model import User
    from server.models.database.holiday_db_model import Holiday
    from server.models.database.calendar_db_model import Calendar


class HolidayCategory(BaseModel, table=True):
    __table_args__ = (
        UniqueConstraint("name", "year", name="unique_holiday_category_name_for_year"),
    )

    name: str = Field()
    year: int = Field()
    created_by_id: int = Field(foreign_key="user.id", default=None)
    created_by: "User" = Relationship(back_populates="holidays_categories")

    holidays: list["Holiday"] = Relationship(
        sa_relationship_kwargs={"cascade": "delete"}, back_populates="category"
    )
    calendars: list["Calendar"] = Relationship(
        back_populates="categories", link_model=CalendarHolidayCategoryLink
    )
