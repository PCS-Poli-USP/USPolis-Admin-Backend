from server.models.dicts.base.role_base_dict import RoleBaseDict
from server.models.dicts.requests.base_requests_dicts import BaseRequestDict
from server.models.http.requests.permission_request_models import PermissionRegister


class RoleRegisterDict(RoleBaseDict, BaseRequestDict, total=False):
    """Role register dictionary."""

    permissions: list[PermissionRegister]


class RoleUpdateDict(RoleRegisterDict, total=False):
    pass
