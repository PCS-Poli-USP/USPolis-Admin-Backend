from src.repository.building_repository import BuildingRepository
from src.repository.user_repository import UserRepository


class BuildingPermissionError(Exception):
    pass


class BuildingRequiredError(Exception):
    pass


class NoSuchBuildingError(Exception):
    pass


def verify_building_permission(username: str, building_id):
    user_repository = UserRepository()
    building_repository = BuildingRepository()

    if building_id is None:
        raise BuildingRequiredError("building_id request param is required")

    building = building_repository.get_by_id(building_id)

    if building is None:
        raise NoSuchBuildingError("Building not found")
    
    building_name = building.get("name")

    logged_user = user_repository.get_by_username(username)
    logged_user_building_ids = [
        str(building["_id"]) for building in logged_user["buildings"]
    ]
    logged_user_is_admin = logged_user.get("isAdmin")
    if building_id not in logged_user_building_ids and not logged_user_is_admin:
        raise BuildingPermissionError(
            "You don't have permission to access this building"
        )
    return building_name
