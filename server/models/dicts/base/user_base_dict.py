from server.models.dicts.base.base_dict import BaseDict


class UserBaseDict(BaseDict, total=False):
    """Base class for user dictionaries (requests and database)\n
    Except for **UserUpdateDict** that is different"""

    is_admin: bool
