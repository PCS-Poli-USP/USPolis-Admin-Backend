from server.models.database.building_permission_db_model import BuildingPermission
from server.models.database.classroom_permission_db_model import ClassroomPermission
from server.models.database.course_permission_db_model import CoursePermission

Permission = ClassroomPermission | CoursePermission | BuildingPermission
PermissionList = (
    list[ClassroomPermission] | list[CoursePermission] | list[BuildingPermission]
)
