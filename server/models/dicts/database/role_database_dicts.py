from datetime import datetime

from server.models.database.user_db_model import User
from server.models.dicts.base.role_base_dict import RoleBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict


class RoleModelDict(RoleBaseDict, BaseModelDict, total=False):
    """TypedDict for Role database model.\n
    This TypedDict is used to define the structure of the Role data.\n
    """

    created_at: datetime
    updated_at: datetime

    # Relationships
    users: list[User]
