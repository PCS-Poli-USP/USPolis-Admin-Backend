from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from server.models.database.api_client_db_model import ApiClient
from server.models.database.api_key_db_model import ApiKey
from server.services.rate_limiter import RateLimitRule
from server.services.security.api_key_crypto import KEY_PREFIX, current_env
from server.services.security.api_key_limits import (
    api_key_status,
    effective_rate_limits,
)
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
