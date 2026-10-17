from enum import StrEnum


class ApiKeyLinkStatus(StrEnum):
    """State of a one-time delivery link, in precedence order. Only
    PENDING links still hold the sealed key."""

    CONSUMED = "consumed"
    INVALIDATED = "invalidated"
    EXPIRED = "expired"
    PENDING = "pending"
