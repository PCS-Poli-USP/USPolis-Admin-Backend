from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, Relationship, Enum
from server.models.database.base_db_model import BaseModel

from server.models.database.class_calendar_link import ClassCalendarLink
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.audiovisual_type_enum import AudiovisualType
from server.utils.enums.class_type import ClassType
from server.utils.must_be_int import must_be_int

if TYPE_CHECKING:
    from server.models.database.calendar_db_model import Calendar
    from server.models.database.schedule_db_model import Schedule
    from server.models.database.subject_db_model import Subject
    from server.models.database.forum_db_model import ForumPost


class Class(BaseModel, table=True):
    __table_args__ = (
        UniqueConstraint("code", "subject_id", name="unique_class_code_for_subject"),
    )
    start_date: date = Field()
    end_date: date = Field()
    code: str = Field()
    professors: list[str] = Field(sa_column=Column(postgresql.ARRAY(String())))
    type: ClassType = Field()
    vacancies: int = Field()

    air_conditionating: bool = Field(default=False)
    accessibility: bool = Field(default=False)
    audiovisual: AudiovisualType = Field(
        sa_column=Column(Enum(AudiovisualType), nullable=False),
        default=AudiovisualType.NONE,
    )

    ignore_to_allocate: bool = Field(default=False)
    full_allocated: bool = Field(default=False)
    updated_at: datetime = Field(default_factory=BrazilDatetime.now_utc)

    subject_id: int = Field(
        foreign_key="subject.id", index=True, default=None, nullable=False
    )

    calendars: list["Calendar"] = Relationship(
        back_populates="classes",
        link_model=ClassCalendarLink,
    )
    schedules: list["Schedule"] = Relationship(
        back_populates="class_",
        sa_relationship_kwargs={"cascade": "all, delete"},
    )
    subject: "Subject" = Relationship(back_populates="classes")
    posts: list["ForumPost"] = Relationship(cascade_delete=True)

    def classroom_ids(self) -> set[int]:
        """
        Get the list of classroom IDs associated with the class schedules.

        Returns:
            list[int]: A list of classroom IDs.
        """
        return {
            must_be_int(schedule.classroom.id)
            for schedule in self.schedules
            if schedule.classroom
        }

    def building_ids(self) -> set[int]:
        """
        Get the list of building IDs associated with the class subject.

        Returns:
            list[int]: A list of building IDs.
        """
        return {must_be_int(building.id) for building in self.subject.buildings}
