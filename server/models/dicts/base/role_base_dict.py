from server.models.dicts.base.base_dict import BaseDict
from server.utils.enums.resources_enums import Resource


class RoleBaseDict(BaseDict, total=False):
    """Base dict for role dictionaries (requests and database)"""

    name: str
    description: str
    resources: list[Resource]
