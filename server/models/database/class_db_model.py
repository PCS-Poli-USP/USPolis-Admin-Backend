from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, Relationship, SQLModel

from server.models.database.class_calendar_link import ClassCalendarLink
from server.utils.enums.class_type import ClassType

if TYPE_CHECKING:
    from server.models.database.calendar_db_model import Calendar
    from server.models.database.schedule_db_model import Schedule
    from server.models.database.subject_db_model import Subject


class Class(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("code", "subject_id", name="unique_class_code_for_subject"),
    )
    id: int | None = Field(default=None, primary_key=True)
    start_date: date = Field()
    end_date: date = Field()
    code: str = Field()
    professors: list[str] = Field(sa_column=Column(postgresql.ARRAY(String())))
    type: ClassType = Field()
    vacancies: int = Field()
    subscribers: int = Field()
    pendings: int = Field()

    air_conditionating: bool = Field(default=False)
    accessibility: bool = Field(default=False)
    projector: bool = Field(default=False)

    ignore_to_allocate: bool = Field(default=False)
    full_allocated: bool = Field(default=False)
    updated_at: datetime = Field(default=datetime.now())

    calendars: Optional[list["Calendar"]] = Relationship(
        back_populates="classes", link_model=ClassCalendarLink,
    )
    schedules: list["Schedule"] = Relationship(back_populates="class_", sa_relationship_kwargs={"cascade": "delete"})

    subject_id: int | None = Field(
        foreign_key="subject.id", index=True, default=None, nullable=False
    )
    subject: "Subject" = Relationship(back_populates="classes")
