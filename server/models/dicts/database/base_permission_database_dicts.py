from datetime import datetime

from server.models.database.role_db_model import Role
from server.models.database.user_db_model import User
from server.models.dicts.database.base_database_dicts import BaseModelDict


class BasePermissionModelDict(BaseModelDict, total=False):
    """TypedDict for the fields shared by every permission database model."""

    role_id: int
    granted_by_id: int
    granted_at: datetime

    # Relationships
    role: Role
    granted_by: User
