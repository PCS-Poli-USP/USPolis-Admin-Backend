from fastapi import status
from fastapi.testclient import TestClient

import pytest
from sqlmodel import Session
from server.repositories.group_repository import GroupNotFound, GroupRepository
from server.repositories.user_repository import UserRepository
from server.utils.must_be_int import must_be_int
from tests.factories.model.group_model_factory import GroupModelFactory
from tests.factories.model.user_model_factory import UserModelFactory
from tests.factories.request.group_request_factory import GroupRequestFactory
from server.models.database.building_db_model import Building
from server.models.database.group_db_model import Group

URL_PREFIX = "/admin/groups"


# Get routes
def test_get_groups_with_admin_user(group: Group, client: TestClient) -> None:
    response = client.get(URL_PREFIX)
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 1


def test_get_groups_with_restricted_user(
    group: Group, restricted_client: TestClient
) -> None:
    response = restricted_client.get(URL_PREFIX)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_groups_with_common_user(group: Group, common_client: TestClient) -> None:
    response = common_client.get(URL_PREFIX)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_group_by_id_with_admin_user(group: Group, client: TestClient) -> None:
    response = client.get(f"{URL_PREFIX}/{group.id}")
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data["id"] == group.id
    assert data["name"] == group.name


def test_get_group_by_id_with_restricted_user(
    group: Group, restricted_client: TestClient
) -> None:
    response = restricted_client.get(f"{URL_PREFIX}/{group.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_group_by_id_with_common_user(
    group: Group, common_client: TestClient
) -> None:
    response = common_client.get(f"{URL_PREFIX}/{group.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_group_with_admin_user(building: Building, client: TestClient) -> None:
    input = GroupRequestFactory(building).create_input()
    response = client.post(URL_PREFIX, json=input.model_dump())
    assert response.status_code == status.HTTP_201_CREATED


def test_create_group_with_users(
    building: Building, session: Session, client: TestClient
) -> None:
    user = UserModelFactory(session).create_and_refresh(buildings=[building])
    input = GroupRequestFactory(building).create_input(user_ids=[must_be_int(user.id)])
    response = client.post(URL_PREFIX, json=input.model_dump())
    assert response.status_code == status.HTTP_201_CREATED

    user = UserRepository.get_by_id(user_id=must_be_int(user.id), session=session)
    assert len(user.groups) == 1
    assert user.groups[0].name == input.name


def test_create_group_with_restricted_user(
    building: Building, restricted_client: TestClient
) -> None:
    input = GroupRequestFactory(building).create_input()
    response = restricted_client.post(URL_PREFIX, json=input.model_dump())

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_group_with_common_user(
    building: Building, common_client: TestClient
) -> None:
    input = GroupRequestFactory(building).create_input()
    response = common_client.post(URL_PREFIX, json=input.model_dump())

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_group_with_admin_user(
    building: Building, session: Session, client: TestClient
) -> None:
    group = GroupModelFactory(building=building, session=session).create_and_refresh()
    input = GroupRequestFactory(building).update_input()
    response = client.put(f"{URL_PREFIX}/{group.id}", json=input.model_dump())

    updated = GroupRepository.get_by_id(
        id=must_be_int(group.id),
        session=session,
    )

    assert response.status_code == status.HTTP_200_OK
    assert updated.name == input.name


def test_update_group_with_restricted_user(
    building: Building, session: Session, restricted_client: TestClient
) -> None:
    group = GroupModelFactory(building=building, session=session).create_and_refresh()
    input = GroupRequestFactory(building).update_input()
    response = restricted_client.put(
        f"{URL_PREFIX}/{group.id}", json=input.model_dump()
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_group_with_common_user(
    building: Building, session: Session, common_client: TestClient
) -> None:
    group = GroupModelFactory(building, session=session).create_and_refresh()
    input = GroupRequestFactory(building).update_input()
    response = common_client.put(f"{URL_PREFIX}/{group.id}", json=input.model_dump())

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_group_with_admin_user(
    building: Building, session: Session, client: TestClient
) -> None:
    group = GroupModelFactory(building, session=session).create_and_refresh()
    response = client.delete(f"{URL_PREFIX}/{group.id}")

    assert response.status_code == status.HTTP_200_OK

    with pytest.raises(GroupNotFound):
        GroupRepository.get_by_id(
            id=must_be_int(group.id),
            session=session,
        )


def test_delete_group_with_restricted_user(
    building: Building, session: Session, restricted_client: TestClient
) -> None:
    group = GroupModelFactory(building, session=session).create_and_refresh()
    response = restricted_client.delete(f"{URL_PREFIX}/{group.id}")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_group_with_common_user(
    building: Building, session: Session, common_client: TestClient
) -> None:
    group = GroupModelFactory(building, session=session).create_and_refresh()
    response = common_client.delete(f"{URL_PREFIX}/{group.id}")

    assert response.status_code == status.HTTP_403_FORBIDDEN
