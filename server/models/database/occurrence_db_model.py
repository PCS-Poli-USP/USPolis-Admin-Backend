from datetime import date as datetime_date
from datetime import time
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from server.models.database.classroom_db_model import Classroom
    from server.models.database.schedule_db_model import Schedule


class Occurrence(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    start_time: time = Field()
    end_time: time = Field()
    date: datetime_date = Field()

    classroom_id: int | None = Field(default=None, foreign_key="classroom.id")
    classroom: "Classroom" = Relationship(back_populates="occurrences")
    schedule_id: int | None = Field(default=None, foreign_key="schedule.id")
    schedule: "Schedule" = Relationship(back_populates="occurrences")
