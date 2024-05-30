from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from server.models.database.subject_building_link import SubjectBuildingLink
from server.models.database.user_building_link import UserBuildingLink

if TYPE_CHECKING:
    from server.models.database.user_db_model import User
    from server.models.database.department_db_model import Department
    from server.models.database.subject_db_model import Subject
    from server.models.database.classroom_db_model import Classroom


class Building(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)

    created_by_id: int | None = Field(default=None, foreign_key="user.id")
    created_by: "User" = Relationship()
    users: list["User"] | None = Relationship(
        back_populates="buildings", link_model=UserBuildingLink
    )
    classrooms: list["Classroom"] | None = Relationship(
        back_populates="building", sa_relationship_kwargs={"cascade": "delete"})
    subjects: list["Subject"] | None = Relationship(
        back_populates="buildings", link_model=SubjectBuildingLink
    )
    departments: list["Department"] | None = Relationship(
        back_populates="building", sa_relationship_kwargs={"cascade": "delete"}
    )
    updated_at: datetime = Field(default=datetime.now())
