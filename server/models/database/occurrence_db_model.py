from datetime import date as datetime_date
from datetime import time
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from server.models.database.classroom_db_model import Classroom
    from server.models.database.schedule_db_model import Schedule


class Occurrence(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    start_time: time = Field(nullable=False)
    end_time: time = Field(nullable=False)
    date: datetime_date = Field()

    classroom_id: int | None = Field(
        default=None, foreign_key="classroom.id", nullable=True
    )
    classroom: Optional["Classroom"] = Relationship(back_populates="occurrences")

    schedule_id: int | None = Field(default=None, index=True, foreign_key="schedule.id")
    schedule: "Schedule" = Relationship(back_populates="occurrences")

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Occurrence):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)

    def conflicts_with(self, other: "Occurrence") -> bool:
        return (
            self.date == other.date
            and self.classroom_id == other.classroom_id
            and self.conflicts_with_time(other.start_time, other.end_time)
        )

    def conflicts_with_time(self, start_time: time, end_time: time) -> bool:
        if self.start_time < start_time and self.end_time > end_time:
            return True
        if self.start_time > start_time and self.start_time < end_time:
            return True
        if self.end_time > start_time and self.end_time < end_time:
            return True
        if start_time < self.start_time and end_time > self.end_time:
            return True
        if self.start_time == start_time and self.end_time == end_time:
            return True
        return False
