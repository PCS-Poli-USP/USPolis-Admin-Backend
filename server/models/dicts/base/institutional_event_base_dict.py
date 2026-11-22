from datetime import datetime

from server.models.dicts.base.base_dict import BaseDict


class InstitutionalEventBaseDict(BaseDict, total=False):
    """Base dict for institutional event dictionaries (requests and database)"""

    title: str
    description: str
    category: str
    start: datetime
    end: datetime
    location: str | None
    building: str | None
    classroom: str | None
    external_link: str | None
