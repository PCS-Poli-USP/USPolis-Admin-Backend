from datetime import datetime
import uuid
from sqlmodel import Field, Relationship, SQLModel

from server.models.database.user_db_model import User
from server.utils.brazil_datetime import BrazilDatetime


class UserSession(SQLModel, table=True):
    # Identifier only (admin screens, deletes): NOT the cookie value. The
    # cookie carries a random token, stored here only as its SHA-256, so a
    # database dump or backup can't be replayed as live sessions. Rows from
    # before the hashing (migration 2c1f0a7d9e34) still have id == their
    # cookie, with token_hash = sha256(id), until they expire.
    id: str = Field(default_factory=lambda: uuid.uuid4().hex, primary_key=True)
    token_hash: str = Field(unique=True, index=True)
    user_id: int = Field(foreign_key="user.id")
    user_agent: str
    ip_address: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=BrazilDatetime.now_utc)

    user: User = Relationship()

    def is_expired(self) -> bool:
        return self.expires_at < BrazilDatetime.now_utc()
