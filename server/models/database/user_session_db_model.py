from datetime import datetime
import uuid
from sqlmodel import Field, Relationship, SQLModel

from server.models.database.user_db_model import User
from server.utils.brazil_datetime import BrazilDatetime


class UserSession(SQLModel, table=True):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user_agent: str
    ip_address: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=BrazilDatetime.now_utc)

    user: User = Relationship()
