from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from server.models.database.base_db_model import BaseModel
from server.models.database.classroom_db_model import Classroom
from server.models.database.group_classroom_link import GroupClassroomLink
from server.models.database.group_user_link import GroupUserLink

if TYPE_CHECKING:
    from server.models.database.user_db_model import User
    from server.models.database.building_db_model import Building


class Group(BaseModel, table=True):
    __table_args__ = (
        UniqueConstraint("building_id", "name", name="unique_group_name_for_building"),
    )

    name: str = Field(index=True, nullable=False, unique=True)
    building_id: int = Field(foreign_key="building.id", nullable=False)
    main: bool = Field(default=False)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

    building: "Building" = Relationship(back_populates="groups")
    classrooms: list[Classroom] = Relationship(link_model=GroupClassroomLink)
    users: list["User"] = Relationship(
        link_model=GroupUserLink, back_populates="groups"
    )
