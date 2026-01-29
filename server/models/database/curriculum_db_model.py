from sqlmodel import Field
from sqlalchemy import Column, ForeignKey, Integer
from server.utils.brazil_datetime import BrazilDatetime
from server.models.database.base_db_model import BaseModel
from datetime import datetime

class Curriculum(BaseModel, table=True):
    course_id: int = Field(
        sa_column=Column(Integer, ForeignKey("course.id", ondelete="CASCADE"),
        nullable=False,)
    )
    emphasis_id: int | None = Field(
        sa_column=Column(Integer, ForeignKey("emphasis.id", ondelete="SET NULL"),
        nullable=True,),
        default=None
    )
    required_class_hours: int = Field()
    required_work_hours: int = Field()
    optional_free_class_hours: int = Field()
    optional_free_work_hours: int = Field()
    optional_elective_class_hours: int = Field()
    optional_elective_work_hours: int = Field()
    AAC: int = Field()
    AEX: int = Field()
    updated_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    updated_by_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    created_by_id: int = Field(foreign_key="user.id")