from server.models.database.classroom_db_model import Classroom
from server.models.dicts.database.base_permission_database_dicts import (
    BasePermissionModelDict,
)
from server.utils.enums.actions_enums import ClassroomAction


class ClassroomPermissionModelDict(BasePermissionModelDict, total=False):
    """TypedDict for ClassroomPermission database model."""

    classroom_id: int | None
    actions: list[ClassroomAction]

    # Relationships
    classroom: Classroom | None
