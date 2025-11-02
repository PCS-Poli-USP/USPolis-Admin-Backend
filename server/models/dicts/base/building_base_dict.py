from server.models.dicts.base.base_dict import BaseDict


class BuildingBaseDict(BaseDict, total=False):
    """Base dict for building dictionaries (requests and database)"""

    name: str
