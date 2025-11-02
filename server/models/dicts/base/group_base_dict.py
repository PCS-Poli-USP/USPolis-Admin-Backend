from server.models.dicts.base.base_dict import BaseDict


class GroupBaseDict(BaseDict, total=False):
    """Base dict for group dictionaries (requests and database)"""

    name: str
    building_id: int
