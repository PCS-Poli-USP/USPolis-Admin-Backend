from typing import TYPE_CHECKING, Optional

from sqlalchemy import Index, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import Enum as SQLEnum
from sqlmodel import Column, Field, Relationship

from server.models.database.base_permission_db_model import BasePermission
from server.utils.enums.actions_enums import ClassroomAction

if TYPE_CHECKING:
    from server.models.database.role_db_model import Role
    from server.models.database.user_db_model import User
    from server.models.database.classroom_db_model import Classroom


class ClassroomPermission(BasePermission, table=True):
    __table_args__ = (
        UniqueConstraint(
            "classroom_id",
            "user_id",
            "role_id",
            name="unique_permission_per_classroom_target",
        ),
        Index(
            "unique_permission_per_classroom_user",
            "classroom_id",
            "user_id",
            unique=True,
            postgresql_where=text("user_id IS NOT NULL"),
        ),
        Index(
            "unique_permission_per_classroom_role",
            "classroom_id",
            "role_id",
            unique=True,
            postgresql_where=text("role_id IS NOT NULL"),
        ),
    )
    classroom_id: int | None = Field(foreign_key="classroom.id")
    actions: list[ClassroomAction] = Field(
        default_factory=list,
        sa_column=Column(
            ARRAY(SQLEnum(ClassroomAction, name="classroomaction")),
            nullable=False,
        ),
    )

    role: Optional["Role"] | None = Relationship(back_populates="classroom_permissions")
    user: Optional["User"] | None = Relationship(
        back_populates="classroom_permissions",
        sa_relationship_kwargs={"foreign_keys": "[ClassroomPermission.user_id]"},
    )

    granted_by: "User" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[ClassroomPermission.granted_by_id]",
            "primaryjoin": "ClassroomPermission.granted_by_id == User.id",
        },
    )
    classroom: Optional["Classroom"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ClassroomPermission.classroom_id]"},
    )
