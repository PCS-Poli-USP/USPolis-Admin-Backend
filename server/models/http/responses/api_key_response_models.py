from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from server.models.database.api_client_db_model import ApiClient
from server.models.database.api_key_db_model import ApiKey
from server.models.database.api_key_delivery_link_db_model import ApiKeyDeliveryLink
from server.services.rate_limiter import RateLimitRule
from server.services.security.api_key_crypto import KEY_PREFIX, current_env
from server.services.security.api_key_link_crypto import delivery_link_url
from server.services.security.api_key_limits import (
    api_key_status,
    effective_rate_limits,
)
from server.utils.enums.api_key_link_status_enum import ApiKeyLinkStatus
from server.utils.enums.api_key_status_enum import ApiKeyStatus
from server.utils.must_be_int import must_be_int


def masked_key(public_id: str) -> str:
    """How a key is shown after creation: identifiable, never usable. Keys
    are only valid in the environment that issued them, so it's this one."""
    return f"{KEY_PREFIX}_{current_env()}_{public_id}_****"


class RateLimitResponse(BaseModel):
    max_requests: int
    window_seconds: int

    @classmethod
    def from_rule(cls, rule: RateLimitRule) -> "RateLimitResponse":
        return cls(max_requests=rule.max_requests, window_seconds=rule.window_seconds)


class ApiKeyDeliveryLinkResponse(BaseModel):
    """A one-time delivery link as the admin sees it: never the token."""

    id: int
    link_id: str
    status: ApiKeyLinkStatus
    expires_at: datetime
    created_by_id: int
    created_at: datetime
    consumed_at: datetime | None
    consumed_ip: str | None
    invalidated_at: datetime | None
    invalidated_by_id: int | None
    emailed_at: datetime | None
    emailed_to: str | None

    @classmethod
    def from_link(cls, link: ApiKeyDeliveryLink) -> "ApiKeyDeliveryLinkResponse":
        return cls(
            id=must_be_int(link.id),
            link_id=link.link_id,
            status=link.status(),
            expires_at=link.expires_at,
            created_by_id=link.created_by_id,
            created_at=link.created_at,
            consumed_at=link.consumed_at,
            consumed_ip=link.consumed_ip,
            invalidated_at=link.invalidated_at,
            invalidated_by_id=link.invalidated_by_id,
            emailed_at=link.emailed_at,
            emailed_to=link.emailed_to,
        )


class ApiKeyResponse(BaseModel):
    id: int
    client_id: int
    name: str
    public_id: str
    masked_key: str
    key_type: Literal["browser", "server"]
    status: ApiKeyStatus
    allowed_path_prefixes: list[str]
    allowed_origins: list[str]
    expires_at: datetime
    # What's actually enforced; `uses_default_limits` = the key has no rows
    # of its own and gets the configured defaults.
    rate_limits: list[RateLimitResponse]
    uses_default_limits: bool
    last_used_at: datetime | None
    revoked_at: datetime | None
    revoked_by_id: int | None
    revoked_reason: str | None
    created_by_id: int
    created_at: datetime
    updated_at: datetime
    # Set when the key was issued for delivery by a one-time link.
    delivery_link: ApiKeyDeliveryLinkResponse | None = None

    @classmethod
    def from_api_key(cls, key: ApiKey) -> "ApiKeyResponse":
        rules, uses_defaults = effective_rate_limits(key)
        return cls(
            id=must_be_int(key.id),
            client_id=key.client_id,
            name=key.name,
            public_id=key.public_id,
            masked_key=masked_key(key.public_id),
            key_type="browser" if key.is_browser_key else "server",
            status=api_key_status(key),
            allowed_path_prefixes=key.allowed_path_prefixes,
            allowed_origins=key.allowed_origins,
            expires_at=key.expires_at,
            rate_limits=[RateLimitResponse.from_rule(rule) for rule in rules],
            uses_default_limits=uses_defaults,
            last_used_at=key.last_used_at,
            revoked_at=key.revoked_at,
            revoked_by_id=key.revoked_by_id,
            revoked_reason=key.revoked_reason,
            created_by_id=key.created_by_id,
            created_at=key.created_at,
            updated_at=key.updated_at,
            delivery_link=ApiKeyDeliveryLinkResponse.from_link(key.delivery_link)
            if key.delivery_link is not None
            else None,
        )

    @classmethod
    def from_api_keys(cls, keys: list[ApiKey]) -> list["ApiKeyResponse"]:
        return [cls.from_api_key(key) for key in keys]


class ApiKeyCreatedResponse(ApiKeyResponse):
    """The only response that carries the key itself: it is never stored
    and can't be retrieved again. Deliver it to the partner securely."""

    key: str

    @classmethod
    def from_created(cls, key: ApiKey, plaintext: str) -> "ApiKeyCreatedResponse":
        return cls(**ApiKeyResponse.from_api_key(key).model_dump(), key=plaintext)


class ApiKeyLinkCreatedResponse(BaseModel):
    """A key issued for delivery by link. Carries the link (with its token)
    instead of the key: in this mode the admin never sees the key."""

    key: ApiKeyResponse
    link: ApiKeyDeliveryLinkResponse
    # Only here, once: the server never stores it.
    token: str
    url: str

    @classmethod
    def from_created(
        cls, key: ApiKey, link: ApiKeyDeliveryLink, token: str
    ) -> "ApiKeyLinkCreatedResponse":
        return cls(
            key=ApiKeyResponse.from_api_key(key),
            link=ApiKeyDeliveryLinkResponse.from_link(link),
            token=token,
            url=delivery_link_url(link.link_id, token),
        )


class ApiKeyLinkPublicResponse(BaseModel):
    """What the partner's page shows before revealing: no secret."""

    status: ApiKeyLinkStatus
    # Pending, and its key can still be used.
    available: bool
    expires_at: datetime
    client_name: str
    key_name: str

    @classmethod
    def from_link(cls, link: ApiKeyDeliveryLink) -> "ApiKeyLinkPublicResponse":
        link_status = link.status()
        return cls(
            status=link_status,
            available=link_status == ApiKeyLinkStatus.PENDING
            and link.api_key.is_usable(),
            expires_at=link.expires_at,
            client_name=link.api_key.client.name,
            key_name=link.api_key.name,
        )


class ApiKeyRevealedResponse(BaseModel):
    """The key itself, shown to the partner once, with what it may do."""

    key: str
    key_name: str
    client_name: str
    expires_at: datetime
    allowed_path_prefixes: list[str]
    allowed_origins: list[str]

    @classmethod
    def from_revealed(
        cls, link: ApiKeyDeliveryLink, plaintext: str
    ) -> "ApiKeyRevealedResponse":
        key = link.api_key
        return cls(
            key=plaintext,
            key_name=key.name,
            client_name=key.client.name,
            expires_at=key.expires_at,
            allowed_path_prefixes=key.allowed_path_prefixes,
            allowed_origins=key.allowed_origins,
        )


class ApiClientResponse(BaseModel):
    id: int
    name: str
    organization: str | None
    contact_name: str
    contact_email: str
    description: str
    is_active: bool
    active_keys: int
    total_keys: int
    created_by_id: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_api_client(cls, client: ApiClient) -> "ApiClientResponse":
        return cls(
            id=must_be_int(client.id),
            name=client.name,
            organization=client.organization,
            contact_name=client.contact_name,
            contact_email=client.contact_email,
            description=client.description,
            is_active=client.is_active,
            active_keys=sum(
                api_key_status(key) == ApiKeyStatus.ACTIVE for key in client.keys
            ),
            total_keys=len(client.keys),
            created_by_id=client.created_by_id,
            created_at=client.created_at,
            updated_at=client.updated_at,
        )

    @classmethod
    def from_api_clients(cls, clients: list[ApiClient]) -> list["ApiClientResponse"]:
        return [cls.from_api_client(client) for client in clients]
