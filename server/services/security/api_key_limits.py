"""Effective rate limits and status of a partner API key."""

from datetime import datetime

from server.config import CONFIG
from server.models.database.api_key_db_model import ApiKey
from server.services.rate_limiter import RateLimitRule, parse_rate_limits
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.api_key_status_enum import ApiKeyStatus


def default_rate_limits(*, browser_key: bool) -> list[RateLimitRule]:
    return parse_rate_limits(
        CONFIG.api_key_browser_default_limits
        if browser_key
        else CONFIG.api_key_default_limits
    )


def effective_rate_limits(key: ApiKey) -> tuple[list[RateLimitRule], bool]:
    """The rules actually enforced for `key`, and whether they're the
    configured defaults (a key without its own rows is never unlimited)."""
    if key.rate_limits:
        return [limit.to_rule() for limit in key.rate_limits], False
    return default_rate_limits(browser_key=key.is_browser_key), True


def api_key_status(key: ApiKey, now: datetime | None = None) -> ApiKeyStatus:
    now = now if now is not None else BrazilDatetime.now_utc()
    if key.revoked_at is not None:
        return ApiKeyStatus.REVOKED
    if not key.client.is_active:
        return ApiKeyStatus.CLIENT_INACTIVE
    if key.expires_at <= now:
        return ApiKeyStatus.EXPIRED
    return ApiKeyStatus.ACTIVE
