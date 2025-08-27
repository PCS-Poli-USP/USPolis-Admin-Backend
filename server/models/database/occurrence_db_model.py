from datetime import date as datetime_date
from datetime import time
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from server.models.database.base_db_model import BaseModel

if TYPE_CHECKING:
    from server.models.database.classroom_db_model import Classroom
    from server.models.database.schedule_db_model import Schedule


class Occurrence(BaseModel, table=True):
    start_time: time = Field(nullable=False)
    end_time: time = Field(nullable=False)
    date: datetime_date = Field()

    classroom_id: int | None = Field(
        default=None, foreign_key="classroom.id", nullable=True
    )
    classroom: Optional["Classroom"] = Relationship(back_populates="occurrences")

    schedule_id: int = Field(default=None, index=True, foreign_key="schedule.id")
    schedule: "Schedule" = Relationship(back_populates="occurrences")

    def conflicts_with(self, other: "Occurrence") -> bool:
        return (
            self.date == other.date
            and self.classroom_id == other.classroom_id
            and self.conflicts_with_time(other.start_time, other.end_time)
        )

    def conflicts_with_time_and_date(
        self, start_time: time, end_time: time, date: datetime_date
    ) -> bool:
        return self.date == date and self.conflicts_with_time(start_time, end_time)

    def conflicts_with_time(self, start_time: time, end_time: time) -> bool:
        if self.start_time < start_time and self.end_time > end_time:
            return True
        if self.start_time < start_time and self.end_time > start_time:
            return True
        if self.start_time > start_time and self.start_time < end_time:
            return True
        if self.start_time > start_time and self.end_time < end_time:
            return True
        if self.start_time == start_time or self.end_time == end_time:
            return True
        return False
