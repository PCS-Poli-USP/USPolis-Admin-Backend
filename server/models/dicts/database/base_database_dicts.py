from server.models.dicts.base.base_dict import BaseDict


class BaseModelDict(BaseDict, total=False):
    id: int | None
