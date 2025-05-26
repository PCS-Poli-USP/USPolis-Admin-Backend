from fastapi import status
from fastapi.testclient import TestClient
from server.models.database.building_db_model import Building


URL_PREFIX = "/buildings"


def test_get_building_by_id_with_admin_user(
    building: Building, client: TestClient
) -> None:
    response = client.get(f"{URL_PREFIX}/{building.id}")
    read = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert read["id"] == building.id
    assert read["name"] == building.name


def test_get_building_by_id_with_restricted_user(
    building: Building, restricted_client: TestClient
) -> None:
    response = restricted_client.get(f"{URL_PREFIX}/{building.id}")
    read = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert read["id"] == building.id
    assert read["name"] == building.name


def test_get_building_by_id_with_common_user(
    building: Building, common_client: TestClient
) -> None:
    response = common_client.get(f"{URL_PREFIX}/{building.id}")

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_get_building_by_id_with_public_user(
    building: Building, public_client: TestClient
) -> None:
    response = public_client.get(f"{URL_PREFIX}/{building.id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
