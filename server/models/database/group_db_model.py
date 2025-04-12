from datetime import datetime
from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

from server.models.database.classroom_db_model import Classroom
from server.models.database.group_classroom_link import GroupClassroomLink
from server.models.database.group_user_link import GroupUserLink

if TYPE_CHECKING:
    from server.models.database.user_db_model import User


class Group(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    abbreviation: str = Field(max_length=10, min_length=3)
    updated_at: datetime = Field(default=datetime.now())
    created_at: datetime = Field(default=datetime.now())

    classrooms: list[Classroom] = Relationship(link_model=GroupClassroomLink)
    users: list["User"] = Relationship(
        link_model=GroupUserLink, back_populates="groups"
    )
