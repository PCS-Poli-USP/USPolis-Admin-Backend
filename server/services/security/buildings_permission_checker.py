from fastapi import HTTPException
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User
from server.services.security.base_permission_checker import PermissionChecker


class BuildingPermissionChecker(PermissionChecker[Building]):
    """
    Class to check permissions for buildings.
    """

    def __init__(self, user: User, session: Session) -> None:
        super().__init__(user=user, session=session)

    def check_permission(
        self, object: int | Building | list[int] | list[Building]
    ) -> None:
        """
        Checks the permission of a user for a specific building.

        Parameters:
        - user (User): The user object for which the permission needs to be checked.
        - building (int | Building | list[int] | list[Building]): The building ID, Building object, list of building IDs, or list of Building objects for which the permission needs to be checked.
        """
        if self.user.is_admin:
            return
        if isinstance(object, int):
            self.__building_id_permission_checker(object)
        elif isinstance(object, Building):
            self.__building_obj_permission_checker(object)
        elif isinstance(object, list):
            self.__building_list_permission_checker(object)

    def __building_id_permission_checker(self, building_id: int) -> None:
        if self.user.buildings is None or building_id not in [
            building.id for building in self.user.buildings
        ]:
            raise ForbiddenBuildingAccess(
                f"Usuário não tem permissão para acessar o prédio com ID {building_id}"
            )

    def __building_obj_permission_checker(self, building: Building) -> None:
        if self.user.buildings is None or building not in self.user.buildings:
            raise ForbiddenBuildingAccess(
                f"Usuário não tem permissão para acessar o prédio {building.name}"
            )

    def __building_list_permission_checker(
        self, buildings: list[int] | list[Building]
    ) -> None:
        allowed = True
        if self.user.buildings is not None:
            building_ids = [
                building.id if isinstance(building, Building) else building
                for building in buildings
            ]
            user_building_ids = [building.id for building in self.user.buildings]
            building_set = set(building_ids)
            user_set = set(user_building_ids)
            if not building_set.issubset(user_set):
                allowed = False
        else:
            allowed = False

        if not allowed:
            names = ", ".join(
                [
                    building.name
                    if isinstance(building, Building)
                    else "ID " + str(building)
                    for building in buildings
                ]
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
