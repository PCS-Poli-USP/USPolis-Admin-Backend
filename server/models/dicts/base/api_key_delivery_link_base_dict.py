from datetime import datetime

from server.models.dicts.base.base_dict import BaseDict


class ApiKeyDeliveryLinkBaseDict(BaseDict, total=False):
    """Base dict for API key delivery link dictionaries"""

    expires_at: datetime
