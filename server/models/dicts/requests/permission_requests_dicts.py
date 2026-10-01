from server.models.dicts.base.permission_base_dict import PermissionBaseDict
from server.models.dicts.requests.base_requests_dicts import BaseRequestDict


class PermissionRegisterDict(PermissionBaseDict, BaseRequestDict, total=False):
    pass


class PermissionUpdateDict(PermissionRegisterDict, total=False):
    pass
