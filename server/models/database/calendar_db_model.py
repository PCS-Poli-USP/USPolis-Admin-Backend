from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from server.models.database.calendar_holiday_category_link import (
    CalendarHolidayCategoryLink,
)
from server.models.database.schedule_calendar_link import ScheduleCalendarLink

if TYPE_CHECKING:
    from server.models.database.holiday_category_db_model import HolidayCategory
    from server.models.database.schedule_db_model import Schedule
    from server.models.database.user_db_model import User


class Calendar(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)

    categories: list["HolidayCategory"] = Relationship(
        back_populates="calendars", link_model=CalendarHolidayCategoryLink
    )
    schedules: list[Schedule] | None = Relationship(
        back_populates="calendars", link_model=ScheduleCalendarLink
    )
    created_by_id: int | None = Field(default=None, foreign_key="user.id")
    created_by: "User" = Relationship(back_populates="calendars")
