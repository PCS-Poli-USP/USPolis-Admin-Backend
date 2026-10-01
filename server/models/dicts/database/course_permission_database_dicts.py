from server.models.database.course_db_model import Course
from server.models.dicts.database.base_permission_database_dicts import (
    BasePermissionModelDict,
)
from server.utils.enums.actions_enums import CourseAction


class CoursePermissionModelDict(BasePermissionModelDict, total=False):
    """TypedDict for CoursePermission database model."""

    course_id: int | None
    actions: list[CourseAction]

    # Relationships
    course: Course | None
