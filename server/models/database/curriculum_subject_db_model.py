from typing import TYPE_CHECKING

from sqlmodel import Field, Enum, Relationship
from server.models.database.base_db_model import BaseModel
from sqlalchemy import UniqueConstraint, Column
from server.utils.enums.curriculum_subject_type_enum import CurriculumSubjectType

if TYPE_CHECKING:
    from server.models.database.curriculum_db_model import Curriculum
    from server.models.database.subject_db_model import Subject


class CurriculumSubject(BaseModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "curriculum_id", "subject_id", name="unique_subject_for_curriculum"
        ),
    )
    curriculum_id: int = Field(foreign_key="curriculum.id")
    subject_id: int = Field(foreign_key="subject.id")
    type: CurriculumSubjectType = Field(
        sa_column=Column(
            Enum(CurriculumSubjectType, name="curriculum_subject_type"), nullable=False
        ),
    )
    period: int = Field()  # Ideal period to take the subject
    curriculum: "Curriculum" = Relationship(back_populates="subjects")
    subject: "Subject" = Relationship(back_populates="curriculum_subjects")
