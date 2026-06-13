from typing import TYPE_CHECKING, Optional

from sqlalchemy import Index, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import Enum as SQLEnum
from sqlmodel import Column, Field, Relationship

from server.models.database.base_permission_db_model import BasePermission
from server.utils.enums.actions_enums import CourseAction

if TYPE_CHECKING:
    from server.models.database.role_db_model import Role
    from server.models.database.user_db_model import User
    from server.models.database.course_db_model import Course


class CoursePermission(BasePermission, table=True):
    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "user_id",
            "role_id",
            name="unique_permission_per_course_target",
        ),
        Index(
            "unique_permission_per_course_user",
            "course_id",
            "user_id",
            unique=True,
            postgresql_where=text("user_id IS NOT NULL"),
        ),
        Index(
            "unique_permission_per_course_role",
            "course_id",
            "role_id",
            unique=True,
            postgresql_where=text("role_id IS NOT NULL"),
        ),
    )
    course_id: int | None = Field(default=None, foreign_key="course.id")
    actions: list[CourseAction] = Field(
        default_factory=list,
        sa_column=Column(
            ARRAY(SQLEnum(CourseAction, name="courseaction")),
            nullable=False,
        ),
    )

    role: Optional["Role"] | None = Relationship(back_populates="course_permissions")
    user: Optional["User"] | None = Relationship(
        back_populates="course_permissions",
        sa_relationship_kwargs={"foreign_keys": "[CoursePermission.user_id]"},
    )

    granted_by: "User" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[CoursePermission.granted_by_id]",
            "primaryjoin": "CoursePermission.granted_by_id == User.id",
        },
    )
    course: Optional["Course"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[CoursePermission.course_id]"},
    )
