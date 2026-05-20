from datetime import datetime

from sqlmodel import Field

from server.models.database.base_db_model import BaseModel
from server.utils.brazil_datetime import BrazilDatetime


class UserRole(BaseModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    role_id: int = Field(foreign_key="role.id", primary_key=True)

    granted_by_id: int = Field(default=None, foreign_key="user.id", nullable=False)
    granted_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
