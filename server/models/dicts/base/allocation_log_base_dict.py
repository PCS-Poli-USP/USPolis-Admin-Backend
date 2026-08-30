from server.models.dicts.base.base_dict import BaseDict
from server.utils.enums.action_type_enum import ActionType


class AllocationLogBaseDict(BaseDict, total=False):
    """Base dict for allocation log dictionaries (requests and database)"""

    user_email: str
    modified_by: str
    action: ActionType
    old_classroom: str
    old_building: str
    new_classroom: str
    new_building: str
