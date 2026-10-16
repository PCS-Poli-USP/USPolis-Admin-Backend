from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from server.models.database.base_db_model import BaseModel
from server.utils.brazil_datetime import BrazilDatetime

if TYPE_CHECKING:
    from server.models.database.api_key_db_model import ApiKey
    from server.models.database.user_db_model import User


class ApiClient(BaseModel, table=True):
    """A partner consuming the API with keys (see docs/API_KEYS.md). Not a
    USPolis user: keys never act on behalf of one."""

    __table_args__ = (UniqueConstraint("name", name="unique_api_client_name"),)

    name: str
    organization: str | None = Field(default=None)
    contact_name: str
    # Who to warn about leaks, revocations and expiring keys.
    contact_email: str
    description: str = Field(default="")
    # Kill switch: an inactive client's keys are all rejected at once.
    is_active: bool = Field(default=True)
    created_by_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    updated_at: datetime = Field(default_factory=BrazilDatetime.now_utc)

    keys: list["ApiKey"] = Relationship(
        back_populates="client",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    created_by: "User" = Relationship()
