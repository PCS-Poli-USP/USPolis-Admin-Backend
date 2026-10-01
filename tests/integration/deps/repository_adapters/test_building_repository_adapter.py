import pytest
from sqlmodel import Session

from server.deps.owned_building_ids import owned_building_ids
from server.deps.repository_adapters.building_repository_adapter import (
    BuildingAlreadyExists,
    BuildingRepositoryAdapter,
)
from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User
from server.services.security.buildings_permission_checker import (
    ForbiddenBuildingAccess,
)
from server.services.security.role_permission_evaluator import build_permission_index
from server.utils.enums.actions_enums import BuildingAction
from server.utils.must_be_int import must_be_int
from tests.factories.request.building_request_factory import BuildingRequestFactory
from tests.utils.permission_test_utils import RolePermissionTestHelper


def _adapter(*, user: User, session: Session) -> BuildingRepositoryAdapter:
    return BuildingRepositoryAdapter(
        owned_building_ids=owned_building_ids(user=user, session=session),
        session=session,
        user=user,
        permission_index=build_permission_index(user),
    )


class TestGetAll:
    def test_admin_sees_every_building(
        self, admin_user: User, building: Building, session: Session
    ) -> None:
        adapter = _adapter(user=admin_user, session=session)

        buildings = adapter.get_all()

        assert building.id in [b.id for b in buildings]

    def test_common_user_sees_none_without_access(
        self, common_user: User, building: Building, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)

        buildings = adapter.get_all()

        assert building.id not in [b.id for b in buildings]


class TestGetById:
    def test_denies_without_permission(
        self, common_user: User, building: Building, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)

        with pytest.raises(ForbiddenBuildingAccess):
            adapter.get_by_id(must_be_int(building.id))

    def test_allows_via_granted_permission(
        self, admin_user: User, common_user: User, building: Building, session: Session
    ) -> None:
        RolePermissionTestHelper.grant_building_permission(
            user=common_user,
            resource_id=must_be_int(building.id),
            actions=[BuildingAction.READ],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)

        found = adapter.get_by_id(must_be_int(building.id))

        assert found.id == building.id


class TestGetByName:
    def test_denies_without_permission(
        self, common_user: User, building: Building, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)

        with pytest.raises(ForbiddenBuildingAccess):
            adapter.get_by_name(building.name)

    def test_allows_via_granted_permission(
        self, admin_user: User, common_user: User, building: Building, session: Session
    ) -> None:
        RolePermissionTestHelper.grant_building_permission(
            user=common_user,
            resource_id=must_be_int(building.id),
            actions=[BuildingAction.READ],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)

        found = adapter.get_by_name(building.name)

        assert found.id == building.id


class TestCreate:
    def test_denies_without_creation_permission(
        self, common_user: User, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)
        input = BuildingRequestFactory().create_input()

        with pytest.raises(ForbiddenBuildingAccess):
            adapter.create(input)

    def test_creates_via_wildcard_permission(
        self, admin_user: User, common_user: User, session: Session
    ) -> None:
        RolePermissionTestHelper.grant_building_permission(
            user=common_user,
            resource_id=-1,
            actions=[BuildingAction.CREATE],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)
        input = BuildingRequestFactory().create_input()

        created = adapter.create(input)

        assert created.name == input.name

    def test_raises_on_duplicate_name(
        self, admin_user: User, building: Building, session: Session
    ) -> None:
        adapter = _adapter(user=admin_user, session=session)
        input = BuildingRequestFactory().create_input(name=building.name)

        with pytest.raises(BuildingAlreadyExists):
            adapter.create(input)


class TestUpdate:
    def test_denies_without_permission(
        self, common_user: User, building: Building, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)
        input = BuildingRequestFactory().update_input()

        with pytest.raises(ForbiddenBuildingAccess):
            adapter.update(must_be_int(building.id), input)

    def test_updates_via_granted_permission(
        self, admin_user: User, common_user: User, building: Building, session: Session
    ) -> None:
        RolePermissionTestHelper.grant_building_permission(
            user=common_user,
            resource_id=must_be_int(building.id),
            actions=[BuildingAction.UPDATE],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)
        input = BuildingRequestFactory().update_input(name="Novo Nome")

        updated = adapter.update(must_be_int(building.id), input)

        assert updated.name == "Novo Nome"


class TestDelete:
    def test_denies_without_permission(
        self, common_user: User, building: Building, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)

        with pytest.raises(ForbiddenBuildingAccess):
            adapter.delete(must_be_int(building.id))

    def test_deletes_via_granted_permission(
        self, admin_user: User, common_user: User, building: Building, session: Session
    ) -> None:
        RolePermissionTestHelper.grant_building_permission(
            user=common_user,
            resource_id=must_be_int(building.id),
            actions=[BuildingAction.DELETE],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)
        building_id = must_be_int(building.id)

        adapter.delete(building_id)
        session.commit()

        assert session.get(Building, building_id) is None


class TestGetOwnedBuildings:
    def test_returns_the_users_owned_buildings(
        self, restricted_user: User, building: Building, session: Session
    ) -> None:
        adapter = _adapter(user=restricted_user, session=session)

        buildings = adapter.get_owned_buildings()

        assert [b.id for b in buildings] == [building.id]
