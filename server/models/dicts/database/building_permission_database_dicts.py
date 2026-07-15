from server.models.database.building_db_model import Building
from server.models.dicts.database.base_permission_database_dicts import (
    BasePermissionModelDict,
)
from server.utils.enums.actions_enums import BuildingAction


class BuildingPermissionModelDict(BasePermissionModelDict, total=False):
    """TypedDict for BuildingPermission database model."""

    building_id: int | None
    actions: list[BuildingAction]

    # Relationships
    building: Building | None
