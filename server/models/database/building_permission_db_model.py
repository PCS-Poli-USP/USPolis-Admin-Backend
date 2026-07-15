from typing import TYPE_CHECKING, Optional

from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import Enum as SQLEnum
from sqlmodel import Column, Field, Relationship

from server.models.database.base_permission_db_model import BasePermission
from server.utils.enums.actions_enums import BuildingAction

if TYPE_CHECKING:
    from server.models.database.role_db_model import Role
    from server.models.database.user_db_model import User
    from server.models.database.building_db_model import Building


class BuildingPermission(BasePermission, table=True):
    __table_args__ = (
        UniqueConstraint(
            "building_id",
            "role_id",
            name="unique_permission_per_building_role",
        ),
    )
    building_id: int | None = Field(foreign_key="building.id")
    actions: list[BuildingAction] = Field(
        default_factory=list,
        sa_column=Column(
            ARRAY(SQLEnum(BuildingAction, name="buildingaction")),
            nullable=False,
        ),
    )

    role: "Role" = Relationship(back_populates="building_permissions")

    granted_by: "User" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[BuildingPermission.granted_by_id]",
            "primaryjoin": "BuildingPermission.granted_by_id == User.id",
        },
    )
    building: Optional["Building"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[BuildingPermission.building_id]"},
    )
