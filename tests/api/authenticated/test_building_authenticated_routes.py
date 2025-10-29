from fastapi import status
from fastapi.testclient import TestClient
from server.models.database.building_db_model import Building
from tests.utils.validators.building.building_response_validator import (
    BuildingResponseAsserts,
)

URL_PREFIX = "/buildings"


def test_get_building_by_id_with_admin_user(
    building: Building, client: TestClient
) -> None:
    response = client.get(f"{URL_PREFIX}/{building.id}")
    assert response.status_code == status.HTTP_200_OK
    BuildingResponseAsserts.assert_building_response(response, building)


def test_get_building_by_id_with_restricted_user(
    building: Building, restricted_client: TestClient
) -> None:
    response = restricted_client.get(f"{URL_PREFIX}/{building.id}")
    assert response.status_code == status.HTTP_200_OK
    BuildingResponseAsserts.assert_building_response(response, building)


def test_get_building_by_id_with_common_user(
    building: Building, common_client: TestClient
) -> None:
    response = common_client.get(f"{URL_PREFIX}/{building.id}")
    assert response.status_code == status.HTTP_200_OK
    BuildingResponseAsserts.assert_building_response(response, building)


def test_get_building_by_id_with_public_user(
    building: Building, public_client: TestClient
) -> None:
    response = public_client.get(f"{URL_PREFIX}/{building.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
