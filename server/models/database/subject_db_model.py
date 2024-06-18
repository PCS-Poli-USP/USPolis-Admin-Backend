from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Column, String
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, Relationship, SQLModel

from server.models.database.subject_building_link import SubjectBuildingLink
from server.utils.enums.subject_type import SubjectType

if TYPE_CHECKING:
    from server.models.database.building_db_model import Building
    from server.models.database.class_db_model import Class


class Subject(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    code: str = Field(index=True, unique=True, nullable=False)
    professors: list[str] = Field(sa_column=Column(postgresql.ARRAY(String())))
    type: SubjectType = Field()
    class_credit: int = Field()
    work_credit: int = Field()
    activation: date = Field()
    deactivation: date | None = Field(default=None)

    buildings: list["Building"] = Relationship(
        back_populates="subjects", link_model=SubjectBuildingLink
    )
    classes: list["Class"] = Relationship(back_populates="subject")
