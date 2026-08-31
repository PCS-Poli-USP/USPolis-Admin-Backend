from sqlmodel import Session

from server.deps.owned_building_ids import owned_building_ids
from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User
from tests.factories.model.building_model_factory import BuildingModelFactory


class TestOwnedBuildingIds:
    def test_admin_gets_every_building(
        self, admin_user: User, building: Building, session: Session
    ) -> None:
        other_building = BuildingModelFactory(admin_user, session).create_and_refresh()

        ids = owned_building_ids(user=admin_user, session=session)

        assert building.id in ids
        assert other_building.id in ids

    def test_restricted_user_gets_only_owned_buildings(
        self, restricted_user: User, building: Building, session: Session
    ) -> None:
        other_building = BuildingModelFactory(
            restricted_user, session
        ).create_and_refresh()

        ids = owned_building_ids(user=restricted_user, session=session)

        assert ids == [building.id]
        assert other_building.id not in ids

    def test_common_user_gets_no_buildings(
        self, common_user: User, building: Building, session: Session
    ) -> None:
        ids = owned_building_ids(user=common_user, session=session)

        assert ids == []
