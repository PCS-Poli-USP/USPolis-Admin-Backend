from server.models.database.course_permission_db_model import CoursePermission
from server.repositories.permission_repository import PermissionRepository
from server.utils.enums.actions_enums import CourseAction


class CoursePermissionRepository(PermissionRepository[CoursePermission, CourseAction]):
    model = CoursePermission
    resource_field = "course_id"
