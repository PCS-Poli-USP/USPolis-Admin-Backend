from server.models.dicts.base.base_dict import BaseDict


class HolidayBaseDict(BaseDict, total=False):
    """Base dict for holiday dictionaries (requests and database)"""

    name: str
    category_id: int
