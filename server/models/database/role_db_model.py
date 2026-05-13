from datetime import datetime
from typing import TYPE_CHECKING
from collections.abc import Sequence

from sqlmodel import Field, Relationship, Column

from server.models.database.base_db_model import BaseModel
from server.models.database.base_permission_db_model import BasePermission
from server.models.database.classroom_permission_db_model import ClassroomPermission
from server.models.database.course_permission_db_model import CoursePermission
from server.models.database.user_role_db_model import UserRole
from server.utils.enums.resources_enums import Resource

from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import Enum as SQLEnum

if TYPE_CHECKING:
    from server.models.database.user_db_model import User

from server.utils.brazil_datetime import BrazilDatetime

UnifiedPermissions = BasePermission | ClassroomPermission | CoursePermission


class Role(BaseModel):
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

    users: list["User"] = Relationship(back_populates="roles", link_model=UserRole)

    # Permissions relationships
    classroom_permissions: list[ClassroomPermission] = Relationship(
        back_populates="role"
    )
    course_permissions: list[CoursePermission] = Relationship(back_populates="role")

    def get_resource_permissions(
        self, resource: Resource
    ) -> Sequence[UnifiedPermissions]:
        """Get the permissions of the role for a given resource"""
        if resource not in self.resources:
            return []
        if resource == Resource.CLASSROOM:
            return self.classroom_permissions
        if resource == Resource.COURSE:
            return self.course_permissions
