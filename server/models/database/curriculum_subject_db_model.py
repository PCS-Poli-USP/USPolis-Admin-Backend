from sqlmodel import Field
from server.models.database.base_db_model import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint

from server.utils.enums.curriculum_subject_type import CurriculumSubjectType

class CurriculumSubject(BaseModel, table=True):
    __table_args__ = (
        UniqueConstraint("curriculum_id", "subject_id", name="unique_subject_for_curriculum"),
    )
    curriculum_id: int = Field(
        sa_column=Column(Integer, ForeignKey("curriculum.id", ondelete="CASCADE"),
        nullable=False,)
    )
    subject_id: int = Field(
        sa_column=Column(Integer, ForeignKey("subject.id", ondelete="CASCADE"),
        nullable=False,)
    )
    type: "CurriculumSubjectType" = Field()
    period: int = Field() # Ideal period to take the subject