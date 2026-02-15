from typing import TYPE_CHECKING

from sqlmodel import Field, Enum, Relationship
from sqlalchemy import Column
from datetime import datetime
from server.models.database.base_db_model import BaseModel
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.course_period_type_enum import CoursePeriodType

if TYPE_CHECKING:
    from server.models.database.curriculum_db_model import Curriculum

class Course(BaseModel, table=True):
    name: str = Field(unique=True)
    minimal_duration: int = Field()
    ideal_duration: int = Field()
    maximal_duration: int = Field()
    updated_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    updated_by_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    created_by_id: int = Field(foreign_key="user.id")
    period: CoursePeriodType = Field(
        sa_column=Column(Enum(CoursePeriodType, name="course_period_type"), nullable=False),
    )
    curriculums: list["Curriculum"] = Relationship(
        back_populates="course", sa_relationship_kwargs={"cascade": "all, delete"}
    )