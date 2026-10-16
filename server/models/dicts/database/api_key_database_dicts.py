from datetime import datetime

from server.models.database.api_client_db_model import ApiClient
from server.models.database.api_key_rate_limit_db_model import ApiKeyRateLimit
from server.models.database.user_db_model import User
from server.models.dicts.base.api_key_base_dict import ApiKeyBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict


class ApiKeyModelDict(ApiKeyBaseDict, BaseModelDict, total=False):
    """TypedDict for the ApiKey database model."""

    client_id: int
    public_id: str
    key_hash: str
    hash_version: int
    revoked_at: datetime | None
    revoked_by_id: int | None
    revoked_reason: str | None
    last_used_at: datetime | None
    created_by_id: int
    created_at: datetime
    updated_at: datetime

    # Relationships
    client: ApiClient
    rate_limits: list[ApiKeyRateLimit]
    created_by: User
