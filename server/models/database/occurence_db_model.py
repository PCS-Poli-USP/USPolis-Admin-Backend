from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from server.models.database.classroom_db_model import Classroom
    from server.models.database.schedule_db_model import Schedule

from server.utils.day_time import DayTime


class Ocurrence(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    start_time: DayTime = Field()
    end_time: DayTime = Field()
    date: datetime = Field()

    classroom_id: int | None = Field(
        default=None, foreign_key="classroom.id", nullable=False
    )
    classroom: "Classroom" = Relationship(back_populates="ocurrences")
    schedule_id: int | None = Field(
        default=None, index=True, foreign_key="schedule.id", nullable=False
    )
    schedule: "Schedule" = Relationship(back_populates="ocurrences")
