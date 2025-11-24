from server.models.dicts.base.base_dict import BaseDict


class CalendarBaseDict(BaseDict, total=False):
    """Base dict for calendar dictionaries (requests and database)"""

    name: str
    year: int
