from server.models.dicts.requests.base_requests_dicts import BaseRequestDict


class GroupRegisterDict(BaseRequestDict, total=False):
    """Group register dictionary."""

    name: str
    classroom_ids: list[int]
    user_ids: list[int]


class GroupUpdateDict(GroupRegisterDict, total=False):
    pass
