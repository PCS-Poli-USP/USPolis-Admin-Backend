from server.models.database.classroom_permission_db_model import ClassroomPermission
from server.repositories.permission_repository import PermissionRepository
from server.utils.enums.actions_enums import ClassroomAction


class ClassroomPermissionRepository(
    PermissionRepository[ClassroomPermission, ClassroomAction]
):
    model = ClassroomPermission
    resource_field = "classroom_id"
