from server.models.dicts.base.base_dict import BaseDict


class BuildingBaseDict(BaseDict, total=False):
    name: str
