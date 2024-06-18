from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel

from server.models.database.reservation_db_model import Reservation

if TYPE_CHECKING:
    from server.models.database.class_db_model import Class
    from server.models.database.occurrence_db_model import Occurrence
    from server.models.database.classroom_db_model import Classroom

from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay


class Schedule(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    week_day: WeekDay | None = Field(nullable=True, default=None)
    start_date: datetime = Field()
    end_date: datetime = Field()
    start_time: str = Field(nullable=False)
    end_time: str = Field(nullable=False)
    skip_exceptions: bool = Field(default=False)
    allocated: bool = Field(default=False)
    recurrence: Recurrence = Field()
    all_day: bool = Field(default=False)

    class_id: int | None = Field(foreign_key="class.id", nullable=True)
    class_: Optional["Class"] = Relationship(back_populates="schedules")

    classroom_id: int | None = Field(foreign_key="classroom.id", nullable=True)
    classroom: Optional["Classroom"] = Relationship(back_populates="schedules")

    reservation_id: int | None = Field(foreign_key="reservation.id", nullable=True)
    reservation: Optional["Reservation"] = Relationship(back_populates="schedule")

    occurrences: list["Occurrence"] | None = Relationship(
        back_populates="schedule", sa_relationship_kwargs={"cascade": "delete"}
    )
