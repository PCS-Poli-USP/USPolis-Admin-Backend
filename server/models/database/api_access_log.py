from datetime import datetime

from sqlalchemy import Column, String
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, Relationship
from server.models.database.base_db_model import BaseModel
from server.models.database.user_db_model import User


class APIAccessLog(BaseModel, table=True):
    security_level: str
    endpoint: str
    method: str
    status_code: int
    timestamp: datetime
    ip_address: str | None = None
    response_time_ms: float
    tags: list[str] = Field(
        sa_column=Column(postgresql.ARRAY(String()), nullable=False)
    )
    user_agent: str
    user_id: int | None = Field(default=None, foreign_key="user.id")

    user: User | None = Relationship(back_populates="api_access_logs")
