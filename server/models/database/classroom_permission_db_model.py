from typing import TYPE_CHECKING, Optional

from sqlalchemy import Index, UniqueConstraint, text
from sqlmodel import Field, Column, Enum, Relationship

from server.models.database.base_permission_db_model import BasePermission
from server.utils.enums.actions_enums import ClassroomAction

if TYPE_CHECKING:
    from server.models.database.role_db_model import Role
    from server.models.database.user_db_model import User


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

    role: Optional["Role"] | None = Relationship(back_populates="classroom_permissions")
    user: Optional["User"] | None = Relationship(
        back_populates="classroom_permissions",
        sa_relationship_kwargs={"foreign_keys": "[ClassroomPermission.user_id]"},
    )

    granted_by_user: "User" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[ClassroomPermission.granted_by]",
            "primaryjoin": "ClassroomPermission.granted_by == User.id",
        },
    )
