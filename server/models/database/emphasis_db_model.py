from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship
from server.models.database.base_db_model import BaseModel
from datetime import datetime
from sqlalchemy import UniqueConstraint
from server.utils.brazil_datetime import BrazilDatetime

if TYPE_CHECKING:
    from server.models.database.course_db_model import Course

class Emphasis(BaseModel, table=True):
    __table_args__ = (
        UniqueConstraint("course_id", "name", name="unique_emphasis_name_for_course"),
    )
    course_id: int = Field(foreign_key="course.id")
    name: str = Field()
    updated_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    updated_by_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    created_by_id: int = Field(foreign_key="user.id")
    course: "Course" = Relationship(back_populates="emphases")