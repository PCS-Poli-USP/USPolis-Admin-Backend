from datetime import datetime
from sqlmodel import Field
from typing import TYPE_CHECKING

from server.models.database.base_db_model import BaseModel
from server.utils.brazil_datetime import BrazilDatetime

if TYPE_CHECKING:
    pass


class Comment(BaseModel, table=True):
    comment: str = Field()
    email: str | None = Field(
        default=None,
        nullable=True,
    )
    created_by_id: int | None = Field(
        foreign_key="mobileuser.id",
        default=None,
        nullable=True,
    )
    created_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
