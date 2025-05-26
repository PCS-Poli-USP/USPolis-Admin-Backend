import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.user_db_model import User
from server.models.database.building_db_model import Building
from server.repositories.building_repository import BuildingNotFound, BuildingRepository
from server.repositories.group_repository import GroupRepository
from server.utils.must_be_int import must_be_int
from tests.factories.request.building_request_factory import BuildingRequestFactory


URL_PREFIX = "/admin/buildings"


def test_create_building_with_admin_user(
    user: User, session: Session, client: TestClient
) -> None:
    input = BuildingRequestFactory().create_input()
    body = input.model_dump()
    response = client.post(URL_PREFIX, json=body)
    created = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert created["name"] == input.name
    assert created["created_by"] == user.name

    group = GroupRepository.get_building_main_group(
        building_id=created["id"], session=session
    )
    assert group.name == created["name"]
    assert group.building_id == created["id"]


def test_create_building_with_used_name(building: Building, client: TestClient) -> None:
    input = BuildingRequestFactory().create_input(name=building.name)
    body = input.model_dump()
    response = client.post(URL_PREFIX, json=body)
    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_building_with_restricted_user(restricted_client: TestClient) -> None:
    input = BuildingRequestFactory().create_input()
    body = input.model_dump()
    response = restricted_client.post(URL_PREFIX, json=body)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_building_with_public_user(public_client: TestClient) -> None:
    input = BuildingRequestFactory().create_input()
    body = input.model_dump()
    response = public_client.post(URL_PREFIX, json=body)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_building_with_common_user(common_client: TestClient) -> None:
    input = BuildingRequestFactory().create_input()
    body = input.model_dump()
    response = common_client.post(URL_PREFIX, json=body)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_building_admin_user_with_admin_user(
    building: Building, client: TestClient
) -> None:
    input = BuildingRequestFactory().update_input()
    body = input.model_dump()
    response = client.put(f"{URL_PREFIX}/{building.id}", json=body)
    updated = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert updated["name"] == input.name


def test_update_building_with_used_name(building: Building, client: TestClient) -> None:
    input = BuildingRequestFactory().update_input(name=building.name)
    body = input.model_dump()
    response = client.post(URL_PREFIX, json=body)

    assert response.status_code == status.HTTP_409_CONFLICT


def test_delete_building_admin_user_with_admin_user(
    building: Building, client: TestClient, session: Session
) -> None:
    response = client.delete(f"{URL_PREFIX}/{building.id}")
    assert response.status_code == status.HTTP_200_OK

    with pytest.raises(BuildingNotFound):
        building = BuildingRepository.get_by_id(
            id=must_be_int(building.id), session=session
        )


def test_delete_building_not_found(client: TestClient, session: Session) -> None:
    response = client.delete(f"{URL_PREFIX}/10")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_building_admin_user_with_restricted_user(
    building: Building, restricted_client: TestClient
) -> None:
    response = restricted_client.delete(f"{URL_PREFIX}/{building.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_building_admin_user_with_common_user(
    building: Building, common_client: TestClient
) -> None:
    response = common_client.delete(f"{URL_PREFIX}/{building.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_building_admin_user_with_public_user(
    building: Building, public_client: TestClient
) -> None:
    response = public_client.delete(f"{URL_PREFIX}/{building.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
