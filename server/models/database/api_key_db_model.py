from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, Column, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, Relationship

from server.models.database.api_client_db_model import ApiClient
from server.models.database.api_key_rate_limit_db_model import ApiKeyRateLimit
from server.models.database.base_db_model import BaseModel
from server.utils.brazil_datetime import BrazilDatetime

if TYPE_CHECKING:
    from server.models.database.user_db_model import User


class ApiKey(BaseModel, table=True):
    """A partner API key (see docs/API_KEYS.md). Only the HMAC of the key is
    stored; the plaintext is shown once, at creation."""

    __table_args__ = (
        CheckConstraint(
            "cardinality(allowed_path_prefixes) > 0",
            name="api_key_check_has_path_prefix",
        ),
        CheckConstraint(
            "revoked_by_id IS NULL OR revoked_at IS NOT NULL",
            name="api_key_check_revoked_by_requires_revoked_at",
        ),
        CheckConstraint(
            "expires_at > created_at",
            name="api_key_check_expires_after_created",
        ),
    )

    client_id: int = Field(foreign_key="apiclient.id", ondelete="CASCADE", index=True)
    name: str
    # Non-secret id embedded in the key: lookup + identification in logs.
    public_id: str = Field(max_length=16, unique=True, index=True)
    key_hash: str = Field(max_length=64, unique=True)
    # Which API_KEY_SECRET produced key_hash, so the secret can be rotated
    # without breaking every key at once.
    hash_version: int = Field(default=1)
    # Relative to the app root, e.g. ["/allocations"]; ["/"] = every public route.
    allowed_path_prefixes: list[str] = Field(
        sa_column=Column(ARRAY(String()), nullable=False)
    )
    # Non-empty = browser key. Empty = server key: rejected if an Origin is sent.
    allowed_origins: list[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(String()), nullable=False, server_default="{}"),
    )
    expires_at: datetime
    revoked_at: datetime | None = Field(default=None)
    revoked_by_id: int | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )
    revoked_reason: str | None = Field(default=None)
    last_used_at: datetime | None = Field(default=None)
    created_by_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    updated_at: datetime = Field(default_factory=BrazilDatetime.now_utc)

    client: ApiClient = Relationship(back_populates="keys")
    rate_limits: list[ApiKeyRateLimit] = Relationship(
        back_populates="api_key",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "order_by": "ApiKeyRateLimit.window_seconds",
        },
    )
    created_by: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ApiKey.created_by_id]"}
    )
    revoked_by: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ApiKey.revoked_by_id]"}
    )

    @property
    def is_browser_key(self) -> bool:
        return bool(self.allowed_origins)

    def is_usable(self, now: datetime | None = None) -> bool:
        """Not revoked, not expired, and its client is active."""
        now = now if now is not None else BrazilDatetime.now_utc()
        return (
            self.revoked_at is None and self.expires_at > now and self.client.is_active
        )
