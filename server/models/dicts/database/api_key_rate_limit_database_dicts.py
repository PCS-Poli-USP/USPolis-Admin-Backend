from server.models.database.api_key_db_model import ApiKey
from server.models.dicts.base.api_key_rate_limit_base_dict import (
    ApiKeyRateLimitBaseDict,
)
from server.models.dicts.database.base_database_dicts import BaseModelDict


class ApiKeyRateLimitModelDict(ApiKeyRateLimitBaseDict, BaseModelDict, total=False):
    """TypedDict for the ApiKeyRateLimit database model."""

    api_key_id: int

    # Relationships
    api_key: ApiKey
