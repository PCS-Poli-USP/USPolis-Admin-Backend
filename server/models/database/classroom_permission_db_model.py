from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, ENUM
from sqlmodel import Field, Column, Relationship

from server.models.database.base_db_model import BaseModel
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.classroom_permission_type_enum import ClassroomPermissionType

if TYPE_CHECKING:
    from server.models.database.user_db_model import User
    from server.models.database.classroom_db_model import Classroom


class ClassroomPermission(BaseModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "classroom_id",
            name="unique_classroom_permission_per_user",
        ),
        CheckConstraint(
            "cardinality(permissions) > 0",
            name="ck_permissions_not_empty",
        ),
    )

    user_id: int = Field(foreign_key="user.id")
    classroom_id: int = Field(foreign_key="classroom.id")
    given_by_id: int = Field(foreign_key="user.id")

    permissions: list[ClassroomPermissionType] = Field(
        sa_column=Column(
            ARRAY(
                ENUM(
                    ClassroomPermissionType,
                    name="classroom_permission_type_enum",
                    create_type=False,
                )
            ),
            nullable=False,
        )
    )

    created_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    updated_at: datetime = Field(default_factory=BrazilDatetime.now_utc)

    user: "User" = Relationship(
        back_populates="classroom_permissions",
        sa_relationship_kwargs={"foreign_keys": "[ClassroomPermission.user_id]"},
    )

    given_by: "User" = Relationship(
        back_populates="given_classroom_permissions",
        sa_relationship_kwargs={"foreign_keys": "[ClassroomPermission.given_by_id]"},
    )

    classroom: "Classroom" = Relationship(back_populates="permissions")
