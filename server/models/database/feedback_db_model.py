from datetime import datetime
from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship
from sqlalchemy import Column, Text
from server.models.database.base_db_model import BaseModel
from server.utils.brazil_datetime import BrazilDatetime

if TYPE_CHECKING:
    from server.models.database.user_db_model import User


class Feedback(BaseModel, table=True):
    user_id: int = Field(foreign_key="user.id", nullable=False)
    title: str
    message: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=BrazilDatetime.now_utc)

    user: "User" = Relationship(back_populates="feedbacks")
