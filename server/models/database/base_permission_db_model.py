from datetime import datetime

from sqlmodel import Field

from server.models.database.base_db_model import BaseModel
from server.utils.brazil_datetime import BrazilDatetime


class BasePermission(BaseModel):
    role_id: int = Field(foreign_key="role.id")

    granted_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    granted_by_id: int = Field(default=None, foreign_key="user.id")
