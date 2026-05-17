from datetime import datetime

from sqlalchemy import CheckConstraint
from sqlmodel import Field

from server.models.database.base_db_model import BaseModel
from server.utils.brazil_datetime import BrazilDatetime


class BasePermission(BaseModel):
    __table_args__: tuple[object, ...] = (
        CheckConstraint(
            "(course_id IS NOT NULL) OR (classroom_id IS NOT NULL)",
            name="permission_check_user_or_role",
        ),
    )

    user_id: int | None = Field(default=None, foreign_key="user.id")
    role_id: int | None = Field(default=None, foreign_key="role.id")

    granted_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    granted_by: int = Field(default=None, foreign_key="user.id")
