from datetime import datetime

from server.models.database.api_key_db_model import ApiKey
from server.models.database.user_db_model import User
from server.models.dicts.base.api_client_base_dict import ApiClientBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict


class ApiClientModelDict(ApiClientBaseDict, BaseModelDict, total=False):
    """TypedDict for the ApiClient database model."""

    is_active: bool
    created_by_id: int
    created_at: datetime
    updated_at: datetime

    # Relationships
    keys: list[ApiKey]
    created_by: User
