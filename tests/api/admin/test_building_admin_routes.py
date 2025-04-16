import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.user_db_model import User
from server.models.database.building_db_model import Building
from server.repositories.building_repository import BuildingNotFound, BuildingRepository
from server.utils.must_be_int import must_be_int
from tests.factories.request.building_request_factory import BuildingRequestFactory


URL_PREFIX = "/admin/buildings"


def test_create_building(user: User, client: TestClient) -> None:
    input = BuildingRequestFactory().create_input()
    body = input.model_dump()
    response = client.post(URL_PREFIX, json=body)
    created = response.json()

    assert response.status_code == 200
    assert created["name"] == input.name
    assert created["created_by"] == user.name


def test_update_building(building: Building, client: TestClient) -> None:
    input = BuildingRequestFactory().update_input()
    body = input.model_dump()
    response = client.put(f"{URL_PREFIX}/{building.id}", json=body)
    updated = response.json()

    assert response.status_code == 200
    assert updated["name"] == input.name


def test_delete_building(
    building: Building, client: TestClient, session: Session
) -> None:
    response = client.delete(f"{URL_PREFIX}/{building.id}")
    assert response.status_code == 204

    with pytest.raises(BuildingNotFound):
        building = BuildingRepository.get_by_id(
            id=must_be_int(building.id), session=session
        )
