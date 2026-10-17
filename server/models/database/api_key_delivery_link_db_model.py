from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, Column, LargeBinary
from sqlmodel import Field, Relationship

from server.models.database.base_db_model import BaseModel
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.api_key_link_status_enum import ApiKeyLinkStatus

if TYPE_CHECKING:
    from server.models.database.api_key_db_model import ApiKey
    from server.models.database.user_db_model import User


class ApiKeyDeliveryLink(BaseModel, table=True):
    """A one-time link delivering an API key to its partner (see
    docs/API_KEYS.md, "Entrega por link"). Holds the key sealed with a token
    that only the link's URL has; the sealed fields are wiped once the link
    is consumed, invalidated or expired, but the row stays for the audit."""

    __table_args__ = (
        CheckConstraint(
            "expires_at > created_at",
            name="api_key_delivery_link_check_expires_after_created",
        ),
        CheckConstraint(
            "(consumed_at IS NULL AND invalidated_at IS NULL) OR ciphertext IS NULL",
            name="api_key_delivery_link_check_dead_link_holds_no_secret",
        ),
    )

    api_key_id: int = Field(
        foreign_key="apikey.id", ondelete="CASCADE", unique=True, index=True
    )
    # Non-secret id in the URL path; the token goes in the fragment.
    link_id: str = Field(max_length=16, unique=True, index=True)
    ciphertext: bytes | None = Field(
        default=None, sa_column=Column(LargeBinary, nullable=True)
    )
    nonce: bytes | None = Field(
        default=None, sa_column=Column(LargeBinary, nullable=True)
    )
    salt: bytes | None = Field(
        default=None, sa_column=Column(LargeBinary, nullable=True)
    )
    expires_at: datetime
    created_by_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    consumed_at: datetime | None = Field(default=None)
    consumed_ip: str | None = Field(default=None, max_length=45)
    consumed_user_agent: str | None = Field(default=None, max_length=512)
    # A null invalidated_by_id with invalidated_at set means the system did
    # it (the link expired unopened).
    invalidated_at: datetime | None = Field(default=None)
    invalidated_by_id: int | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )
    emailed_at: datetime | None = Field(default=None)
    emailed_to: str | None = Field(default=None)
    emailed_by_id: int | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )

    api_key: "ApiKey" = Relationship(back_populates="delivery_link")
    created_by: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ApiKeyDeliveryLink.created_by_id]"}
    )
    invalidated_by: Optional["User"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[ApiKeyDeliveryLink.invalidated_by_id]"
        }
    )
    emailed_by: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ApiKeyDeliveryLink.emailed_by_id]"}
    )

    def status(self, now: datetime | None = None) -> ApiKeyLinkStatus:
        now = now if now is not None else BrazilDatetime.now_utc()
        if self.consumed_at is not None:
            return ApiKeyLinkStatus.CONSUMED
        if self.invalidated_at is not None:
            return ApiKeyLinkStatus.INVALIDATED
        if self.expires_at <= now:
            return ApiKeyLinkStatus.EXPIRED
        return ApiKeyLinkStatus.PENDING

    def wipe_secret(self) -> None:
        self.ciphertext = None
        self.nonce = None
        self.salt = None
