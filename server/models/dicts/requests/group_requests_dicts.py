from server.models.dicts.base.group_base_dict import GroupBaseDict
from server.models.dicts.requests.base_requests_dicts import BaseRequestDict


class GroupRegisterDict(GroupBaseDict, BaseRequestDict, total=False):
    """Group register dictionary."""

    classroom_ids: list[int] | None
    user_ids: list[int]


class GroupUpdateDict(GroupRegisterDict, total=False):
    pass
