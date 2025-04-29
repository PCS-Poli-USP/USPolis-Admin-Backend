from server.models.dicts.base.base_dict import BaseDict


class GroupBaseDict(BaseDict, total=False):
    name: str
