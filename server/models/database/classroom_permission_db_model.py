from sqlalchemy import Index, UniqueConstraint, text
from sqlmodel import Field, Column, Enum

from server.models.database.base_permission_db_model import BasePermission
from server.utils.enums.actions_enums import ClassroomAction


class ClassroomPermission(BasePermission, table=True):
    __table_args__ = (
        UniqueConstraint(
            "action",
            "classroom_id",
            "user_id",
            "role_id",
            name="unique_action_per_classroom_permission",
        ),
        Index(
            "unique_action_per_classroom_permission_user",
            "action",
            "classroom_id",
            "user_id",
            unique=True,
            postgresql_where=text("user_id IS NOT NULL"),
        ),
        Index(
            "unique_action_per_classroom_permission_role",
            "action",
            "classroom_id",
            "role_id",
            unique=True,
            postgresql_where=text("role_id IS NOT NULL"),
        ),
    )
    classroom_id: int = Field(foreign_key="classroom.id")
    action: ClassroomAction = Field(
        sa_column=Column(Enum(ClassroomAction), nullable=False)
    )
