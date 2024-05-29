from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from server.models.database.user_building_link import UserBuildingLink

if TYPE_CHECKING:
    from server.models.database.building_db_model import Building


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str
    is_admin: bool
    name: str
    cognito_id: str
    created_by_id: int | None = Field(
        foreign_key="user.id",
        default=None,
        nullable=True,
    )
    created_by: Optional["User"] = Relationship(
        sa_relationship_kwargs=dict(remote_side="User.id"),
    )
    buildings: list["Building"] | None = Relationship(
        back_populates="users", link_model=UserBuildingLink
    )
    updated_at: datetime = Field(default=datetime.now())
