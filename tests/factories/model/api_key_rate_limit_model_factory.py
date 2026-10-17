from typing import Unpack

from sqlmodel import Session

from server.models.database.api_key_db_model import ApiKey
from server.models.database.api_key_rate_limit_db_model import ApiKeyRateLimit
from server.models.dicts.database.api_key_rate_limit_database_dicts import (
    ApiKeyRateLimitModelDict,
)
from server.utils.must_be_int import must_be_int
from tests.factories.base.api_key_rate_limit_base_factory import (
    ApiKeyRateLimitBaseFactory,
)
from tests.factories.model.base_model_factory import BaseModelFactory


class ApiKeyRateLimitModelFactory(BaseModelFactory[ApiKeyRateLimit]):
    def __init__(self, api_key: ApiKey, session: Session) -> None:
        super().__init__(session)
        self.api_key = api_key
        self.core_factory = ApiKeyRateLimitBaseFactory()

    def _get_model_type(self) -> type[ApiKeyRateLimit]:
        return ApiKeyRateLimit

    def get_defaults(self) -> ApiKeyRateLimitModelDict:
        core = self.core_factory.get_base_defaults()
        return {**core, "api_key_id": must_be_int(self.api_key.id)}

    def create(  # type: ignore
        self, **overrides: Unpack[ApiKeyRateLimitModelDict]
    ) -> ApiKeyRateLimit:
        return super().create(**overrides)

    def create_and_refresh(  # type: ignore
        self, **overrides: Unpack[ApiKeyRateLimitModelDict]
    ) -> ApiKeyRateLimit:
        return super().create_and_refresh(**overrides)

    def update(  # type: ignore
        self, rate_limit_id: int, **overrides: Unpack[ApiKeyRateLimitModelDict]
    ) -> ApiKeyRateLimit:
        return super().update(model_id=rate_limit_id, **overrides)
