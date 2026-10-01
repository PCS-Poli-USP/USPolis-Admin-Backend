import pytest
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User
from server.services.security.buildings_permission_checker import (
    BuildingPermissionChecker,
    ForbiddenBuildingAccess,
)
from server.services.security.role_permission_evaluator import build_permission_index
from server.utils.enums.actions_enums import BuildingAction
from server.utils.must_be_int import must_be_int
from tests.factories.model.building_model_factory import BuildingModelFactory
from tests.utils.permission_test_utils import RolePermissionTestHelper


def test_building_checker_denies_without_group_or_role(
    building: Building, common_user: User, session: Session
) -> None:
    checker = BuildingPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )

    with pytest.raises(ForbiddenBuildingAccess):
        checker.check_permission(must_be_int(building.id), BuildingAction.READ)


def test_building_checker_allows_via_role_permission(
    building: Building, admin_user: User, common_user: User, session: Session
) -> None:
    RolePermissionTestHelper.grant_building_permission(
        user=common_user,
        resource_id=must_be_int(building.id),
        actions=[BuildingAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = BuildingPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(must_be_int(building.id), BuildingAction.READ)


def test_building_checker_allows_via_wildcard_role_permission(
    building: Building, admin_user: User, common_user: User, session: Session
) -> None:
    """A wildcard grant (resource_id=-1) is honored for READ even without
    ever specifically granting `building` - it covers every instance of
    the resource, not just the one it happened to be tested against."""
    other_building = BuildingModelFactory(
        creator=admin_user, session=session
    ).create_and_refresh()
    RolePermissionTestHelper.grant_building_permission(
        user=common_user,
        resource_id=-1,
        actions=[BuildingAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = BuildingPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(must_be_int(building.id), BuildingAction.READ)
    checker.check_permission(must_be_int(other_building.id), BuildingAction.READ)


def test_building_checker_denies_creation_without_role(
    common_user: User, session: Session
) -> None:
    checker = BuildingPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )

    with pytest.raises(ForbiddenBuildingAccess):
        checker.check_creation_permission(BuildingAction.CREATE)


def test_building_checker_allows_creation_via_wildcard_role_permission(
    admin_user: User, common_user: User, session: Session
) -> None:
    RolePermissionTestHelper.grant_building_permission(
        user=common_user,
        resource_id=-1,
        actions=[BuildingAction.CREATE],
        granted_by=admin_user,
        session=session,
    )

    checker = BuildingPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_creation_permission(BuildingAction.CREATE)
