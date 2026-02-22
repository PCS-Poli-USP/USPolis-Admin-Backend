from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship
from server.utils.brazil_datetime import BrazilDatetime
from server.models.database.base_db_model import BaseModel
from datetime import datetime

if TYPE_CHECKING:
    from server.models.database.user_db_model import User
    from server.models.database.course_db_model import Course
    from server.models.database.curriculum_subject_db_model import CurriculumSubject


class Curriculum(BaseModel, table=True):
    course_id: int = Field(foreign_key="course.id")
    AAC: int = Field()
    AEX: int = Field()
    updated_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    updated_by_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    created_by_id: int = Field(foreign_key="user.id")
    description: str = Field()
    course: "Course" = Relationship(back_populates="curriculums")
    subjects: list["CurriculumSubject"] = Relationship(
        back_populates="curriculum", sa_relationship_kwargs={"cascade": "all, delete"}
        )
    users: list["User"] = Relationship(
        back_populates="curriculum", sa_relationship_kwargs={"foreign_keys": "[User.curriculum_id]"}
        )