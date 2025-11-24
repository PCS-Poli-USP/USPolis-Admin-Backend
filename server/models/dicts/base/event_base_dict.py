from server.models.dicts.base.base_dict import BaseDict


class EventBaseDict(BaseDict, total=False):
    """Base dict for event dictionaries (requests and database)"""

    link: str | None
