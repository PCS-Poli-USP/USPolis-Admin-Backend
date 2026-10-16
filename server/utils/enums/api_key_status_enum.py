from enum import StrEnum


class ApiKeyStatus(StrEnum):
    """Why a key is (or isn't) accepted, in precedence order."""

    REVOKED = "revoked"
    CLIENT_INACTIVE = "client_inactive"
    EXPIRED = "expired"
    ACTIVE = "active"
