from datetime import datetime

from sqlmodel import Field, UniqueConstraint

from server.models.database.base_db_model import BaseModel
from server.utils.brazil_datetime import BrazilDatetime


class UserRole(BaseModel, table=True):
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="unique_user_role"),)

    user_id: int = Field(foreign_key="user.id")
    role_id: int = Field(foreign_key="role.id")

    granted_by_id: int = Field(default=None, foreign_key="user.id", nullable=False)
    granted_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
