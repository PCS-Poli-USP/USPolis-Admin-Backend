from unittest.mock import MagicMock

import pytest
from sqlmodel import Session
from server.models.database.user_db_model import User
from server.repositories.building_repository import BuildingNotFound, BuildingRepository
from server.utils.must_be_int import must_be_int
from tests.factories.model.building_model_factory import BuildingModelFactory
from tests.factories.request.building_request_factory import BuildingRequestFactory


def test_building_repository_create(user: User, mock_session: MagicMock) -> None:
    """Test the create method of the BuildingRepository.\n
    Tests:\n
    - building is created with the correct values\n
    - session.commit() is not called\n
    - building id is None
    """
    factory = BuildingRequestFactory()
    input = factory.create_input()
    building = BuildingRepository.create(
        building_in=input, creator=user, session=mock_session
    )

    mock_session.commit.assert_not_called()
    assert building.id is None
    assert building.name == input.name


def test_building_repository_get_by_id(user: User, session: Session) -> None:
    """Test the get by id method of the BuildingRepository.\n
    Tests:\n
    - buildings read are the same as the ones created\n
    """
    factory = BuildingModelFactory(user, session)
    building = factory.create_and_refresh()
    query = BuildingRepository.get_by_id(id=must_be_int(building.id), session=session)
    assert query.name == building.name


def test_building_repository_get_all(user: User, session: Session) -> None:
    """Test **get_all** method of the BuildingRepository.\n
    Tests:\n
    - number of buildings get is correct\n
    - buildings read are the same as the ones created\n
    """
    factory = BuildingModelFactory(user, session)
    old_buildings = factory.create_many_default()
    buildings = BuildingRepository.get_all(session=session)

    assert len(buildings) == len(old_buildings)
    for building in buildings:
        assert building in old_buildings


def test_building_repository_get_by_name(user: User, session: Session) -> None:
    """Test **get_by_name** method of the BuildingRepository.\n
    Tests:\n
    - buildings read are the same as the ones created\n
    """
    factory = BuildingModelFactory(user, session)
    building = factory.create_and_refresh()
    query = BuildingRepository.get_by_name(name=building.name, session=session)
    assert query.name == building.name


def test_building_repository_get_by_ids(user: User, session: Session) -> None:
    """Test **get_by_ids** method of the BuildingRepository.\n
    Tests:\n
    - number of buildings read is correct\n
    - all buildings read are in the list of ids\n
    """
    factory = BuildingModelFactory(user, session)
    old_buildings = factory.create_many_default()
    factory.commit()
    factory.refresh_many(old_buildings)
    ids = [must_be_int(building.id) for building in old_buildings]
    buildings = BuildingRepository.get_by_ids(ids=ids, session=session)

    assert len(buildings) == len(old_buildings)
    for building in buildings:
        assert building.id in ids


def test_building_repository_update(user: User, session: Session) -> None:
    """Test **update** method of the BuildingRepository.\n
    Tests:\n
    - building new name is equal input\n
    - building name is different from the old name\n
    """
    factory = BuildingModelFactory(user, session)
    building = factory.create_and_refresh()
    old_name = building.name
    input = BuildingRequestFactory().update_input()
    building = BuildingRepository.update(
        id=must_be_int(building.id), input=input, session=session
    )
    assert building.name == input.name
    assert building.name != old_name


def test_building_repository_delete(user: User, session: Session) -> None:
    """Test **delete** method of the BuildingRepository.\n
    Tests:\n
    - building get by id from old id raises BuildingNotFound\n
    """
    factory = BuildingModelFactory(user, session)
    building = factory.create_and_refresh()
    id = must_be_int(building.id)
    BuildingRepository.delete(id=id, session=session)
    with pytest.raises(
        BuildingNotFound,
    ):
        BuildingRepository.get_by_id(id=id, session=session)
