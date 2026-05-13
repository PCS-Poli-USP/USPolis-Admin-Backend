from sqlalchemy import Index, UniqueConstraint, text
from sqlmodel import Column, Enum, Field

from server.models.database.base_permission_db_model import BasePermission
from server.utils.enums.actions_enums import CourseAction


class CoursePermission(BasePermission, table=True):
    __table_args__ = (
        UniqueConstraint(
            "action",
            "course_id",
            "user_id",
            "role_id",
            name="unique_action_per_course_permission",
        ),
        Index(
            "unique_action_per_course_permission_user",
            "action",
            "course_id",
            "user_id",
            unique=True,
            postgresql_where=text("user_id IS NOT NULL"),
        ),
        Index(
            "unique_action_per_course_permission_role",
            "action",
            "course_id",
            "role_id",
            unique=True,
            postgresql_where=text("role_id IS NOT NULL"),
        ),
    )
    course_id: int | None = Field(default=None, foreign_key="course.id")
    action: CourseAction = Field(sa_column=Column(Enum(CourseAction), nullable=False))
