from typing import Unpack

from server.models.dicts.requests.api_key_requests_dicts import (
    ApiClientRegisterDict,
    ApiClientUpdateDict,
    ApiKeyRegisterDict,
    ApiKeyUpdateDict,
    ApiKeyViaLinkRegisterDict,
)
from server.models.http.requests.api_key_request_models import (
    ApiClientRegister,
    ApiClientUpdate,
    ApiKeyRegister,
    ApiKeyUpdate,
    ApiKeyViaLinkRegister,
    RateLimitRegister,
)
from tests.factories.base.api_client_base_factory import ApiClientBaseFactory
from tests.factories.base.api_key_base_factory import ApiKeyBaseFactory
from tests.factories.request.base_request_factory import BaseRequestFactory


class ApiClientRequestFactory(BaseRequestFactory):
    def __init__(self) -> None:
        super().__init__()
        self.core_factory = ApiClientBaseFactory()

    def get_default_create(self) -> ApiClientRegisterDict:
        return {**self.core_factory.get_base_defaults()}

    def get_default_update(self) -> ApiClientUpdateDict:
        return self.get_default_create()

    def create_input(
        self, **overrides: Unpack[ApiClientRegisterDict]
    ) -> ApiClientRegister:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return ApiClientRegister(**default)

    def update_input(self, **overrides: Unpack[ApiClientUpdateDict]) -> ApiClientUpdate:
        default = self.get_default_update()
        self.override_default_dict(default, overrides)  # type: ignore
        return ApiClientUpdate(**default)


class ApiKeyRequestFactory(BaseRequestFactory):
    def __init__(self) -> None:
        super().__init__()
        self.core_factory = ApiKeyBaseFactory()

    def get_default_update(self) -> ApiKeyUpdateDict:
        return {**self.core_factory.get_base_defaults()}

    def get_default_create(self) -> ApiKeyRegisterDict:
        return {
            **self.get_default_update(),
            "rate_limits": [RateLimitRegister(max_requests=120, window_seconds=60)],
        }

    def create_input(self, **overrides: Unpack[ApiKeyRegisterDict]) -> ApiKeyRegister:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return ApiKeyRegister(**default)

    def update_input(self, **overrides: Unpack[ApiKeyUpdateDict]) -> ApiKeyUpdate:
        default = self.get_default_update()
        self.override_default_dict(default, overrides)  # type: ignore
        return ApiKeyUpdate(**default)

    def get_default_via_link(self) -> ApiKeyViaLinkRegisterDict:
        return {**self.get_default_create(), "link_ttl_hours": 24}

    def create_via_link_input(
        self, **overrides: Unpack[ApiKeyViaLinkRegisterDict]
    ) -> ApiKeyViaLinkRegister:
        default = self.get_default_via_link()
        self.override_default_dict(default, overrides)  # type: ignore
        return ApiKeyViaLinkRegister(**default)  # type: ignore[arg-type]
