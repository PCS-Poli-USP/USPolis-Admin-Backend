from server.models.database.classroom_permission_db_model import ClassroomPermission
from server.models.database.course_permission_db_model import CoursePermission
from server.models.database.building_permission_db_model import BuildingPermission


Permission = ClassroomPermission | CoursePermission | BuildingPermission
PermissionList = (
    list[ClassroomPermission] | list[CoursePermission] | list[BuildingPermission]
)
