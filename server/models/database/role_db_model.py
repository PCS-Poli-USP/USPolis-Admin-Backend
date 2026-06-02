from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, Column

from server.models.database.base_db_model import BaseModel
from server.models.database.building_permission_db_model import BuildingPermission
from server.models.database.classroom_permission_db_model import ClassroomPermission
from server.models.database.course_permission_db_model import CoursePermission
from server.models.database.user_role_db_model import UserRole
from server.utils.enums.resources_enums import Resource

from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import Enum as SQLEnum

from server.utils.permissions_types import Permission

if TYPE_CHECKING:
    from server.models.database.user_db_model import User

from server.utils.brazil_datetime import BrazilDatetime


class Role(BaseModel, table=True):
    name: str
    description: str = Field(default="")
    resources: list[Resource] = Field(
        sa_column=Column(
            ARRAY(
                SQLEnum(
                    Resource,
                    name="resource_enum",
                )
            ),
            nullable=False,
            default=list,
        )
    )
    created_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    updated_at: datetime = Field(default_factory=BrazilDatetime.now_utc)

    users: list["User"] = Relationship(
        back_populates="roles",
        link_model=UserRole,
        sa_relationship_kwargs={
            "primaryjoin": "Role.id == UserRole.role_id",
            "secondaryjoin": "User.id == UserRole.user_id",
        },
    )

    # Permissions relationships
    classroom_permissions: list[ClassroomPermission] = Relationship(
        back_populates="role"
    )
    course_permissions: list[CoursePermission] = Relationship(back_populates="role")
    building_permissions: list[BuildingPermission] = Relationship(back_populates="role")

    def get_permissions(self) -> list[Permission]:
        """Get all permissions of the role"""
        permissions: list[Permission] = []
        permissions.extend(self.classroom_permissions)
        permissions.extend(self.course_permissions)
        permissions.extend(self.building_permissions)
        return permissions

    def get_resource_permissions(self, resource: Resource) -> list[Permission]:
        """Get the permissions of the role for a given resource"""
        if resource not in self.resources:
            return []
        if resource == Resource.CLASSROOM:
            return list(self.classroom_permissions)
        if resource == Resource.COURSE:
            return list(self.course_permissions)
        if resource == Resource.BUILDING:
            return list(self.building_permissions)
        return []

    def get_resource_permissions_map(self) -> dict[Resource, list[Permission]]:
        """Get a map of resource to permissions for the role"""
        permissions_map: dict[Resource, list[Permission]] = {}
        for resource in self.resources:
            permissions_map[resource] = self.get_resource_permissions(resource)
        return permissions_map
