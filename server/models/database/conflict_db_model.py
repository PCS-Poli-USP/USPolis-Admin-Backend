from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel
from datetime import date as datetime_date

from server.models.database.classroom_db_model import Classroom


class Conflict(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "fist_occurrence_id",
            "second_occurrence_id",
            "first_schedule_id",
            "second_schedule_id",
            name="unique_conflict_schedule_occurrence_tuple",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    date: datetime_date
    classroom_id: int = Field(foreign_key="classroom.id")
    fist_occurrence_id: int = Field(foreign_key="occurrence.id")
    second_occurrence_id: int = Field(foreign_key="occurrence.id")
    first_schedule_id: int = Field(foreign_key="schedule.id")
    second_schedule_id: int = Field(foreign_key="schedule.id")

    classroom: Classroom = Relationship(back_populates="conflicts")
