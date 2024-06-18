from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel, Column, Enum
from sqlalchemy import String
from sqlalchemy.dialects import postgresql

from server.models.database.subject_building_link import SubjectBuildingLink
from server.utils.enums.subject_type import SubjectType

if TYPE_CHECKING:
    from server.models.database.building_db_model import Building
    from server.models.database.class_db_model import Class


class Subject(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    code: str = Field(index=True, unique=True, nullable=False)
    professors: list[str] = Field(
        sa_column=Column(postgresql.ARRAY(String()), nullable=False)
    )
    type: SubjectType = Field(sa_column=Column(Enum(SubjectType)))
    class_credit: int = Field(nullable=False)
    work_credit: int = Field(nullable=False)
    activation: datetime = Field(nullable=False)
    desactivation: datetime | None = Field(default=None)

    buildings: list["Building"] = Relationship(
        back_populates="subjects", link_model=SubjectBuildingLink
    )
    classes: list["Class"] = Relationship(back_populates="subject")
