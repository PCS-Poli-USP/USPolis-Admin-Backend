from fastapi import status
from fastapi.testclient import TestClient

import pytest
from sqlmodel import Session
from server.repositories.group_repository import GroupNotFound, GroupRepository
from server.utils.must_be_int import must_be_int
from tests.factories.model.group_model_factory import GroupModelFactory
from tests.factories.request.group_request_factory import GroupRequestFactory
from server.models.database.building_db_model import Building

URL_PREFIX = "/admin/groups"


def test_create_group_with_admin_user(building: Building, client: TestClient) -> None:
    input = GroupRequestFactory(building).create_input()
    response = client.post(URL_PREFIX, json=input.model_dump())
    assert response.status_code == status.HTTP_201_CREATED


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
