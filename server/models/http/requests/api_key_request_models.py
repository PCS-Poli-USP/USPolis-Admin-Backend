from datetime import datetime, timedelta
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from server.config import CONFIG
from server.services.security.api_key_scope import (
    validate_origin,
    validate_path_prefix,
)
from server.utils.brazil_datetime import BrazilDatetime

MAX_KEY_LIFETIME = timedelta(days=365)


class ApiClientRegister(BaseModel):
    name: str = Field(min_length=1, max_length=256)
    organization: str | None = None
    contact_name: str = Field(min_length=1, max_length=256)
    contact_email: EmailStr
    description: str = ""


class ApiClientUpdate(ApiClientRegister):
    pass


class RateLimitRegister(BaseModel):
    max_requests: int = Field(gt=0)
    window_seconds: int = Field(gt=0)


class ApiKeyUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=256)
    allowed_path_prefixes: list[str] = Field(min_length=1)
    allowed_origins: list[str] = Field(default_factory=list)
    expires_at: datetime

    @field_validator("allowed_path_prefixes")
    @classmethod
    def validate_prefixes(cls, prefixes: list[str]) -> list[str]:
        return list(dict.fromkeys(validate_path_prefix(p) for p in prefixes))

    @field_validator("allowed_origins")
    @classmethod
    def validate_origins(cls, origins: list[str]) -> list[str]:
        # http://localhost is only for testing a partner site locally.
        allow_local = CONFIG.environment.strip().lower() != "production"
        return list(
            dict.fromkeys(
                validate_origin(o, allow_insecure_localhost=allow_local)
                for o in origins
            )
        )

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at(cls, expires_at: datetime) -> datetime:
        # Stored like every other timestamp: naive Brazil local time.
        if expires_at.tzinfo is not None:
            expires_at = expires_at.astimezone(BrazilDatetime.brazil_tz()).replace(
                tzinfo=None
            )
        now = BrazilDatetime.now_utc()
        if expires_at <= now:
            raise ValueError("A data de expiração deve estar no futuro")
        if expires_at > now + MAX_KEY_LIFETIME:
            raise ValueError("Uma chave pode valer por no máximo 365 dias")
        return expires_at


class ApiKeyRateLimitsUpdate(BaseModel):
    # Empty = the configured defaults (API_KEY_DEFAULT_LIMITS or
    # API_KEY_BROWSER_DEFAULT_LIMITS), never unlimited.
    rate_limits: list[RateLimitRegister] = Field(default_factory=list)

    @field_validator("rate_limits")
    @classmethod
    def validate_unique_windows(
        cls, limits: list[RateLimitRegister]
    ) -> list[RateLimitRegister]:
        windows = [limit.window_seconds for limit in limits]
        if len(set(windows)) != len(windows):
            raise ValueError("Cada janela de rate limit só pode aparecer uma vez")
        return limits


class ApiKeyRegister(ApiKeyUpdate, ApiKeyRateLimitsUpdate):
    pass


# How long a one-time delivery link stays open (see docs/API_KEYS.md).
ApiKeyLinkTtlHours = Literal[1, 24, 72]


class ApiKeyViaLinkRegister(ApiKeyRegister):
    link_ttl_hours: ApiKeyLinkTtlHours = 24


class ApiKeyLinkEmailSend(BaseModel):
    # The link's token, which only the admin's screen holds: the server
    # never stores it, so it can't rebuild the link on its own.
    token: str = Field(min_length=1, max_length=128)
    message: str | None = Field(default=None, max_length=1000)


class ApiKeyLinkReveal(BaseModel):
    token: str = Field(min_length=1, max_length=128)


class ApiKeyRevoke(BaseModel):
    # Kept on the key for the audit trail, e.g. "vazou no GitHub".
    reason: str = Field(min_length=3, max_length=500)


class ApiClientActiveUpdate(BaseModel):
    is_active: bool
