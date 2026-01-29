from sqlmodel import Field
from server.models.database.base_db_model import BaseModel
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from server.utils.brazil_datetime import BrazilDatetime

class Emphasis(BaseModel, table=True):
    __table_args__ = (
        UniqueConstraint("course_id", "name", name="unique_emphasis_name_for_course"),
    )
    course_id: int = Field(
        sa_column=Column(Integer, ForeignKey("course.id", ondelete="CASCADE"),
        nullable=False,)
    )
    name: str = Field()
    updated_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    updated_by_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    created_by_id: int = Field(foreign_key="user.id")