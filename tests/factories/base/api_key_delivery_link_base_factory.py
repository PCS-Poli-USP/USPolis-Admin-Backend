from datetime import timedelta

from server.models.dicts.base.api_key_delivery_link_base_dict import (
    ApiKeyDeliveryLinkBaseDict,
)
from server.utils.brazil_datetime import BrazilDatetime
from tests.factories.base.base_factory import BaseFactory


class ApiKeyDeliveryLinkBaseFactory(BaseFactory):
    """Base factory for API key delivery links. Defaults to a pending link
    valid for 24 hours."""

    def get_base_defaults(self) -> ApiKeyDeliveryLinkBaseDict:
        return {
            "expires_at": BrazilDatetime.now_utc() + timedelta(hours=24),
        }
