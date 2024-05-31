from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Column, String
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, Relationship, SQLModel

from server.models.database.department_classroom_link import DepartmentClassroomLink


if TYPE_CHECKING:
    from server.models.database.building_db_model import Building
    from server.models.database.subject_db_model import Subject
    from server.models.database.classroom_db_model import Classroom


class Department(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    abbreviation: str = Field(index=True, unique=True)
    professors: list[str] = Field(sa_column=Column(postgresql.ARRAY(String())))
    updated_at: datetime = Field(default=datetime.now())

    building_id: int | None = Field(
        foreign_key="building.id", default=None, nullable=False
    )
    building: "Building" = Relationship(back_populates="departments")
    classrooms: list["Classroom"] | None = Relationship(
        back_populates="departments", link_model=DepartmentClassroomLink
    )
    subjects: list["Subject"] | None = Relationship(back_populates="department")
