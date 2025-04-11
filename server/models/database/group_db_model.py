from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

from server.models.database.classroom_db_model import Classroom
from server.models.database.group_classroom_link import GroupClassroomLink


class Group(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    abbreviation: str = Field(max_length=10)
    updated_at: datetime = Field(default=datetime.now())
    created_at: datetime = Field(default=datetime.now())

    classrooms: list[Classroom] = Relationship(link_model=GroupClassroomLink)
