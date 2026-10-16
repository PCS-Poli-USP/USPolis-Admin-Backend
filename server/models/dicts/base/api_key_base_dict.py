from datetime import datetime

from server.models.dicts.base.base_dict import BaseDict


class ApiKeyBaseDict(BaseDict, total=False):
    """Base dict for API key dictionaries (requests and database)"""

    name: str
    allowed_path_prefixes: list[str]
    allowed_origins: list[str]
    expires_at: datetime
