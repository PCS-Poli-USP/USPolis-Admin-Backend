from server.models.dicts.base.base_dict import BaseDict
from server.utils.enums.actions_enums import PermissionAction
from server.utils.enums.resources_enums import Resource


class PermissionBaseDict(BaseDict, total=False):
    """Base dict for permission dictionaries (requests and database)"""

    resource: Resource
    resource_id: int
    actions: list[PermissionAction]
    role_id: int
