from server.models.database.building_permission_db_model import BuildingPermission
from server.repositories.permission_repository import PermissionRepository
from server.utils.enums.actions_enums import BuildingAction


class BuildingPermissionRepository(
    PermissionRepository[BuildingPermission, BuildingAction]
):
    model = BuildingPermission
    resource_field = "building_id"
