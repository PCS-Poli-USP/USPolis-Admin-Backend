from datetime import datetime
from typing import TYPE_CHECKING, Optional

from fastapi import HTTPException, status
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from server.models.database.base_db_model import BaseModel
from server.models.database.subject_building_link import SubjectBuildingLink
from server.models.database.user_building_link import UserBuildingLink
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.must_be_int import must_be_int

if TYPE_CHECKING:
    from server.models.database.classroom_db_model import Classroom
    from server.models.database.subject_db_model import Subject
    from server.models.database.user_db_model import User
    from server.models.database.classroom_solicitation_db_model import (
        ClassroomSolicitation,
    )
    from server.models.database.group_db_model import Group


class Building(BaseModel, table=True):
    __table__args__ = (UniqueConstraint("main_group_id", name="unique_main_group_id"),)

    name: str = Field(index=True, unique=True)
    updated_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    created_by_id: int | None = Field(default=None, foreign_key="user.id")
    main_group_id: int | None = Field(default=None, foreign_key="group.id")

    created_by: "User" = Relationship()
    users: list["User"] | None = Relationship(
        back_populates="buildings", link_model=UserBuildingLink
    )
    classrooms: list["Classroom"] = Relationship(
        back_populates="building", sa_relationship_kwargs={"cascade": "delete"}
    )
    subjects: list["Subject"] | None = Relationship(
        back_populates="buildings", link_model=SubjectBuildingLink
    )
    solicitations: list["ClassroomSolicitation"] = Relationship(
        back_populates="building", sa_relationship_kwargs={"cascade": "delete"}
    )
    main_group: Optional["Group"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[Building.main_group_id]",
            "cascade": "delete",
            "post_update": True,
        }
    )
    groups: list["Group"] = Relationship(
        back_populates="building",
        sa_relationship_kwargs={
            "cascade": "delete",
            "foreign_keys": "[Group.building_id]",
        },
    )

    def get_main_group(self) -> "Group":
        """Get the main group of the building.\n
        Raises:
            BuildingWithouMainGroup: If the building has no main group. That is a invalid building, a building must have a main group that is created on building creation.
        """
        if not self.main_group:
            raise BuildingWithouMainGroup()
        return self.main_group

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

    def get_users(self) -> list["User"]:
        """
        Get the list of users who have access to the building.

        Returns:
            List of User objects.
        """
        users: set[User] = set()
        for group in self.groups:
            users.update(group.users)
        return list(users)


class BuildingWithouMainGroup(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Building has no main group",
        )
