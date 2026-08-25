from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, String, Text
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, Relationship, Enum

from server.models.database.base_db_model import BaseModel
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.api_security_level_enum import APISecurityLevel

if TYPE_CHECKING:
    from server.models.database.user_db_model import User


class ApiAccessLog(BaseModel, table=True):
    security_level: APISecurityLevel = Field(
        sa_column=Column(Enum(APISecurityLevel), nullable=False)
    )
    endpoint: str = Field(nullable=False)
    method: str = Field(nullable=False)
    status_code: int = Field(nullable=False, index=True)
    timestamp: datetime = Field(default_factory=BrazilDatetime.now_utc, index=True)
    ip_address: str | None = Field(default=None, nullable=True)
    user_agent: str | None = Field(default=None, nullable=True)
    response_time_ms: int | None = Field(default=None, nullable=True)
    tags: list[str] = Field(
        sa_column=Column(postgresql.ARRAY(String()), nullable=False, server_default="{}")
    )
    user_id: int | None = Field(default=None, foreign_key="user.id", nullable=True)
    detail: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    request_body: str | None = Field(default=None, sa_column=Column(Text, nullable=True))

    user: "User" = Relationship()
