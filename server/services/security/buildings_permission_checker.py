from fastapi import HTTPException
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User
from server.services.security.base_permission_checker import PermissionChecker
from server.services.security.role_permission_evaluator import PermissionIndex
from server.utils.enums.actions_enums import PermissionAction
from server.utils.enums.resources_enums import Resource
from server.utils.must_be_int import must_be_int


class BuildingPermissionChecker(PermissionChecker[Building]):
    """
    Class to check permissions for buildings.
    """

    def __init__(
        self, user: User, session: Session, permission_index: PermissionIndex
    ) -> None:
        super().__init__(user=user, session=session)
        self.permission_index = permission_index

    def check_permission(  # type: ignore[override]
        self,
        object: int | Building | list[int] | list[Building],
        action: PermissionAction,
    ) -> None:
        """
        Checks the permission of a user for a specific building.

        Parameters:
        - object (int | Building | list[int] | list[Building]): The building ID, Building object, list of building IDs, or list of Building objects for which the permission needs to be checked.
        - action (PermissionAction): The action being performed on the building(s).
        """
        if self.user.is_admin:
            return
        if isinstance(object, int):
            self.__building_id_permission_checker(object, action)
        elif isinstance(object, Building):
            self.__building_obj_permission_checker(object, action)
        elif isinstance(object, list):
            self.__building_list_permission_checker(object, action)

    def check_creation_permission(self, action: PermissionAction) -> None:
        """Check permission to create a new building. There's no existing id/Group
        membership to check against, so this only honors a Role-granted wildcard
        permission (or admin) — never a Group-based one, since Group never modeled
        "who may create buildings", only membership in existing ones."""
        if self.user.is_admin:
            return
        if not self.permission_index.has_permission(
            resource=Resource.BUILDING, action=action, resource_id=None
        ):
            raise ForbiddenBuildingAccess(
                "Usuário não tem permissão para criar prédios"
            )

    def is_allowed(self, building_id: int, action: PermissionAction) -> bool:
        """Non-raising version of check_permission, for callers that need to test
        several buildings and decide what to do themselves (e.g. "any of these")."""
        group_allows = self.user.buildings is not None and building_id in [
            must_be_int(building.id) for building in self.user.buildings
        ]
        return group_allows or self.permission_index.has_permission(
            resource=Resource.BUILDING, action=action, resource_id=building_id
        )

    def __building_id_permission_checker(
        self, building_id: int, action: PermissionAction
    ) -> None:
        if not self.is_allowed(building_id, action):
            raise ForbiddenBuildingAccess(
                f"Usuário não tem permissão para acessar o prédio com ID {building_id}"
            )

    def __building_obj_permission_checker(
        self, building: Building, action: PermissionAction
    ) -> None:
        if not self.is_allowed(must_be_int(building.id), action):
            raise ForbiddenBuildingAccess(
                f"Usuário não tem permissão para acessar o prédio {building.name}"
            )

    def __building_list_permission_checker(
        self, buildings: list[int] | list[Building], action: PermissionAction
    ) -> None:
        disallowed = [
            building
            for building in buildings
            if not self.is_allowed(
                must_be_int(building.id) if isinstance(building, Building) else building,
                action,
            )
        ]
        if disallowed:
            names = ", ".join(
                building.name if isinstance(building, Building) else "ID " + str(building)
                for building in disallowed
            )
            raise ForbiddenBuildingAccess(
                f"Usuário não tem permissão para acessar um ou mais prédios: {names}"
            )


class ForbiddenBuildingAccess(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=403,
            detail=detail,
        )
