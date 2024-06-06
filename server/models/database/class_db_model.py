from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, String
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, Relationship, SQLModel

from server.utils.enums.class_type import ClassType

if TYPE_CHECKING:
    from server.models.database.schedule_db_model import Schedule
    from server.models.database.subject_db_model import Subject


class Class(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    period: list[str] = Field(sa_column=Column(postgresql.ARRAY(String())))
    start_date: datetime = Field()
    end_date: datetime = Field()
    class_type: ClassType = Field()
    vacancies: int = Field()
    subscribers: int = Field()
    pendings: int = Field()

    air_conditionating: bool = Field(default=False)
    accessibility: bool = Field(default=False)
    projector: bool = Field(default=False)

    ignore_to_allocate: bool = Field(default=False)
    full_allocated: bool = Field(default=False)
    updated_at: datetime = Field(default=datetime.now())

    schedules: list["Schedule"] | None = Relationship(back_populates="university_class")

    subject_id: int | None = Field(
        foreign_key="subject.id", index=True, default=None, nullable=False
    )
    subject: "Subject" = Relationship(back_populates="classes")
