from datetime import timedelta

from server.models.dicts.base.api_key_base_dict import ApiKeyBaseDict
from server.utils.brazil_datetime import BrazilDatetime
from tests.factories.base.base_factory import BaseFactory


class ApiKeyBaseFactory(BaseFactory):
    """Base factory for API key model or request. Defaults to a server key
    (no origins) scoped to the allocation routes, valid for 90 days."""

    def get_base_defaults(self) -> ApiKeyBaseDict:
        return {
            "name": self.faker.unique.bs(),
            "allowed_path_prefixes": ["/allocations"],
            "allowed_origins": [],
            "expires_at": BrazilDatetime.now_utc() + timedelta(days=90),
        }
