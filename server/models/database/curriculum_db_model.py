from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship
from server.utils.brazil_datetime import BrazilDatetime
from server.models.database.base_db_model import BaseModel
from datetime import datetime

if TYPE_CHECKING:
    from server.models.database.course_db_model import Course
    from server.models.database.curriculum_subject_db_model import CurriculumSubject

class Curriculum(BaseModel, table=True):
    course_id: int = Field(foreign_key="course.id")
    emphasis_id: int | None = Field(foreign_key="emphasis.id", default=None)
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
    course: "Course" = Relationship(back_populates="curriculums")
    subjects: list["CurriculumSubject"] = Relationship(
        back_populates="curriculum", sa_relationship_kwargs={"cascade": "all, delete"}
        )