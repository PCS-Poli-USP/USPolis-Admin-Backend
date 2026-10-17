from server.models.dicts.base.api_key_rate_limit_base_dict import (
    ApiKeyRateLimitBaseDict,
)
from tests.factories.base.base_factory import BaseFactory


class ApiKeyRateLimitBaseFactory(BaseFactory):
    """Base factory for an API key rate limit (model or request)."""

    def get_base_defaults(self) -> ApiKeyRateLimitBaseDict:
        return {"max_requests": 120, "window_seconds": 60}
