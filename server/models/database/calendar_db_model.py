from collections.abc import Generator
from datetime import date
from typing import TYPE_CHECKING, Any

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship
from server.models.database.base_db_model import BaseModel

from server.models.database.calendar_holiday_category_link import (
    CalendarHolidayCategoryLink,
)
from server.models.database.class_calendar_link import ClassCalendarLink

if TYPE_CHECKING:
    from server.models.database.class_db_model import Class
    from server.models.database.holiday_category_db_model import HolidayCategory
    from server.models.database.user_db_model import User


class Calendar(BaseModel, table=True):
    __table_args__ = (
        UniqueConstraint("name", "year", name="unique_calendar_name_for_year"),
    )
    name: str = Field()
    year: int = Field()
    categories: list["HolidayCategory"] = Relationship(
        back_populates="calendars", link_model=CalendarHolidayCategoryLink
    )
    classes: list["Class"] = Relationship(
        back_populates="calendars", link_model=ClassCalendarLink
    )
    created_by_id: int | None = Field(default=None, foreign_key="user.id")
    created_by: "User" = Relationship(back_populates="calendars")

    def dates(self) -> Generator[date, Any, None]:
        for category in self.categories:
            for holiday in category.holidays:
                yield holiday.date
