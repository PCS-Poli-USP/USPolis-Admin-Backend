from server.models.dicts.base.permission_base_dict import PermissionBaseDict
from server.utils.enums.actions_enums import (
    BuildingAction,
    ClassroomAction,
    CourseAction,
    PermissionAction,
)
from server.utils.enums.resources_enums import Resource
from tests.factories.base.base_factory import BaseFactory

DEFAULT_ACTIONS_BY_RESOURCE: dict[Resource, list[PermissionAction]] = {
    Resource.BUILDING: [BuildingAction.READ],
    Resource.CLASSROOM: [ClassroomAction.READ],
    Resource.COURSE: [CourseAction.READ],
}


class PermissionBaseFactory(BaseFactory):
    """Base factory for permission model or permission request.\n
    A default permission grants read access to every resource of the given type (resource_id = -1) to the given role.
    """

    def __init__(self, role_id: int, resource: Resource) -> None:
        super().__init__()
        self.role_id = role_id
        self.resource = resource

    def get_base_defaults(self) -> PermissionBaseDict:
        """Return base default values common to models and requests"""
        return {
            "resource": self.resource,
            "resource_id": -1,
            "actions": list(DEFAULT_ACTIONS_BY_RESOURCE[self.resource]),
            "role_id": self.role_id,
        }
