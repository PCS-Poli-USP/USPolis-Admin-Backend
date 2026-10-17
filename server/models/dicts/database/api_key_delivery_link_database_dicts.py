from datetime import datetime

from server.models.database.api_key_db_model import ApiKey
from server.models.database.user_db_model import User
from server.models.dicts.base.api_key_delivery_link_base_dict import (
    ApiKeyDeliveryLinkBaseDict,
)
from server.models.dicts.database.base_database_dicts import BaseModelDict


class ApiKeyDeliveryLinkModelDict(
    ApiKeyDeliveryLinkBaseDict, BaseModelDict, total=False
):
    """TypedDict for the ApiKeyDeliveryLink database model."""

    api_key_id: int
    link_id: str
    ciphertext: bytes | None
    nonce: bytes | None
    salt: bytes | None
    created_by_id: int
    created_at: datetime
    consumed_at: datetime | None
    consumed_ip: str | None
    consumed_user_agent: str | None
    invalidated_at: datetime | None
    invalidated_by_id: int | None
    emailed_at: datetime | None
    emailed_to: str | None
    emailed_by_id: int | None

    # Relationships
    api_key: ApiKey
    created_by: User
