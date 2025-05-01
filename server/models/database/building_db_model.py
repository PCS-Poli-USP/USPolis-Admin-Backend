from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from server.models.database.subject_building_link import SubjectBuildingLink
from server.models.database.user_building_link import UserBuildingLink
from server.utils.must_be_int import must_be_int

if TYPE_CHECKING:
    from server.models.database.classroom_db_model import Classroom
    from server.models.database.subject_db_model import Subject
    from server.models.database.user_db_model import User
    from server.models.database.classroom_solicitation_db_model import (
        ClassroomSolicitation,
    )
    from server.models.database.group_db_model import Group


class Building(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by_id: int | None = Field(default=None, foreign_key="user.id")

    created_by: "User" = Relationship()
    users: list["User"] | None = Relationship(
        back_populates="buildings", link_model=UserBuildingLink
    )
    classrooms: list["Classroom"] | None = Relationship(
        back_populates="building", sa_relationship_kwargs={"cascade": "delete"}
    )
    subjects: list["Subject"] | None = Relationship(
        back_populates="buildings", link_model=SubjectBuildingLink
    )
    solicitations: list["ClassroomSolicitation"] = Relationship(
        back_populates="building"
    )
    groups: list["Group"] = Relationship(
        back_populates="building", sa_relationship_kwargs={"cascade": "delete"}
    )

    def get_classrooms_ids_set(self) -> set[int]:
        """
        Get the set of classroom IDs in the building.

        Returns:
            set[int]: A set of classroom IDs.
        """
        return (
            {must_be_int(classroom.id) for classroom in self.classrooms}
            if self.classrooms
            else set()
        )
