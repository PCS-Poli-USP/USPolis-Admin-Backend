from server.models.dicts.base.api_client_base_dict import ApiClientBaseDict
from server.models.dicts.base.api_key_base_dict import ApiKeyBaseDict
from server.models.dicts.requests.base_requests_dicts import BaseRequestDict
from server.models.http.requests.api_key_request_models import RateLimitRegister


class ApiClientRegisterDict(ApiClientBaseDict, BaseRequestDict, total=False):
    """API client register dictionary."""


class ApiClientUpdateDict(ApiClientRegisterDict, total=False):
    pass


class ApiKeyUpdateDict(ApiKeyBaseDict, BaseRequestDict, total=False):
    """API key update dictionary."""


class ApiKeyRegisterDict(ApiKeyUpdateDict, total=False):
    """API key register dictionary."""

    rate_limits: list[RateLimitRegister]
