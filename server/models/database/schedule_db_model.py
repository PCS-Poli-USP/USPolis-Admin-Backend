from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column
from sqlmodel import Field, Relationship, SQLModel

from server.models.database.reservation_db_model import Reservation
from server.models.database.schedule_calendar_link import ScheduleCalendarLink

if TYPE_CHECKING:
    from server.models.database.calendar_db_model import Calendar
    from server.models.database.class_db_model import Class
    from server.models.database.occurrence_db_model import Occurrence

from server.utils.day_time import DayTime, DayTimeType
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay


class Schedule(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    week_day: WeekDay = Field()
    start_date: datetime = Field()
    end_date: datetime = Field()
    start_time: DayTime = Field(sa_column=Column(DayTimeType))
    end_time: DayTime = Field(sa_column=Column(DayTimeType))
    skip_exceptions: bool = Field(default=False)
    allocated: bool = Field(default=False)
    recurrence: Recurrence = Field()
    all_day: bool = Field(default=False)

    university_class_id: int | None = Field(foreign_key="class.id", nullable=True)
    university_class: Optional["Class"] = Relationship(back_populates="schedules")

    reservation: Optional["Reservation"] = Relationship(back_populates="schedule")

    occurrences: list["Occurrence"] = Relationship(back_populates="schedule")
    calendars: list["Calendar"] = Relationship(
        back_populates="schedules", link_model=ScheduleCalendarLink
    )
