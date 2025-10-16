from server.models.dicts.base.base_dict import BaseDict


class HolidayCategoryBaseDict(BaseDict, total=False):
    """Base dict for holiday category dictionaries (requests and database)"""

    name: str
    year: int
