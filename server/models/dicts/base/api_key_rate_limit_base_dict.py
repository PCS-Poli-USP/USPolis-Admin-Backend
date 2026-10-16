from server.models.dicts.base.base_dict import BaseDict


class ApiKeyRateLimitBaseDict(BaseDict, total=False):
    """Base dict for API key rate limit dictionaries (requests and database)"""

    max_requests: int
    window_seconds: int
