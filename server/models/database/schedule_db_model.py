from datetime import date, time
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship, desc

from server.models.database.base_db_model import BaseModel
from server.models.database.reservation_db_model import Reservation
from server.models.database.allocation_log_db_model import AllocationLog

if TYPE_CHECKING:
    from server.models.database.class_db_model import Class
    from server.models.database.classroom_db_model import Classroom
    from server.models.database.occurrence_db_model import Occurrence

from server.utils.enums.month_week import MonthWeek
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay


class Schedule(BaseModel, table=True):
    start_date: date = Field(index=True)
    end_date: date = Field(index=True)
    start_time: time = Field()
    end_time: time = Field()
    week_day: WeekDay | None = Field(nullable=True, default=None)
    allocated: bool = Field(default=False)
    recurrence: Recurrence = Field()
    month_week: MonthWeek | None = Field(default=None, nullable=True)
    all_day: bool = Field(default=False)

    class_id: int | None = Field(
        sa_column=Column(Integer, ForeignKey("class.id", ondelete="CASCADE")),
        default=None,
    )
    class_: Optional["Class"] = Relationship(back_populates="schedules")

    classroom_id: int | None = Field(
        foreign_key="classroom.id", nullable=True, default=None
    )
    classroom: Optional["Classroom"] = Relationship(back_populates="schedules")

    reservation_id: int | None = Field(
        default=None, foreign_key="reservation.id", nullable=True
    )
    reservation: Optional["Reservation"] = Relationship(back_populates="schedule")

    occurrences: list["Occurrence"] = Relationship(
        back_populates="schedule",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    logs: list[AllocationLog] = Relationship(
        sa_relationship_kwargs={
            "cascade": "all, delete",
            "order_by": lambda: desc(AllocationLog.modified_at),
        },
    )
