from fastapi import status
from fastapi.testclient import TestClient

import pytest
from sqlmodel import Session

from server.models.database.user_db_model import User
from server.models.database.building_db_model import Building

from server.repositories.classroom_repository import (
    ClassroomNotFound,
    ClassroomRepository,
)
from server.repositories.group_repository import GroupRepository
from server.utils.must_be_int import must_be_int
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.model.group_model_factory import GroupModelFactory
from tests.factories.request.classroom_request_factory import ClassroomRequestFactory


URL_PREFIX = "/classrooms"


def test_get_classroom_by_id_with_admin_user(
    user: User, building: Building, session: Session, client: TestClient
) -> None:
    created = ClassroomModelFactory(
        creator=user, building=building, session=session
    ).create_and_refresh()

    response = client.get(f"{URL_PREFIX}/{created.id}")
    classroom = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert classroom["id"] == created.id
    assert classroom["name"] == created.name
    assert classroom["floor"] == created.floor
    assert classroom["capacity"] == created.capacity
    assert classroom["audiovisual"] == created.audiovisual


def test_get_classroom_by_id_with_restricted_user(
    restricted_user: User,
    user: User,
    building: Building,
    session: Session,
    restricted_client: TestClient,
) -> None:
    created = ClassroomModelFactory(
        creator=user, building=building, session=session
    ).create_and_refresh()
    GroupModelFactory(session=session).create_and_refresh(
        classrooms=[created], users=[restricted_user]
    )
    response = restricted_client.get(f"{URL_PREFIX}/{created.id}")
    classroom = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert classroom["id"] == created.id
    assert classroom["name"] == created.name
    assert classroom["floor"] == created.floor
    assert classroom["capacity"] == created.capacity
    assert classroom["audiovisual"] == created.audiovisual


def test_get_classroom_by_id_with_common_user(
    user: User, building: Building, session: Session, common_client: TestClient
) -> None:
    created = ClassroomModelFactory(
        creator=user, building=building, session=session
    ).create_and_refresh()
    response = common_client.get(f"{URL_PREFIX}/{created.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_classroom_with_admin_user(
    user: User, building: Building, client: TestClient
) -> None:
    input = ClassroomRequestFactory(building=building).create_input()
    body = input.model_dump()
    response = client.post(URL_PREFIX, json=body)
    created = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert created["name"] == input.name
    assert created["created_by"] == user.name
    assert created["building_id"] == building.id


def test_create_classroom_with_restricted_user(
    restricted_user: User,
    building: Building,
    session: Session,
    restricted_client: TestClient,
) -> None:
    input = ClassroomRequestFactory(building=building).create_input()
    body = input.model_dump()
    group = GroupModelFactory(session).create_and_refresh(users=[restricted_user])

    response = restricted_client.post(URL_PREFIX, json=body)
    created = response.json()

    new_group = GroupRepository.get_by_id(id=must_be_int(group.id), session=session)
    assert len(new_group.classrooms) == 1
    assert new_group.classrooms[0].id == created["id"]

    assert response.status_code == status.HTTP_200_OK
    assert created["name"] == input.name
    assert created["created_by"] == restricted_user.name
    assert created["building_id"] == building.id


def test_create_classroom_with_common_user(
    building: Building, common_client: TestClient
) -> None:
    input = ClassroomRequestFactory(building=building).create_input()
    body = input.model_dump()
    response = common_client.post(URL_PREFIX, json=body)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_classroom_with_admin_user(
    user: User, building: Building, session: Session, client: TestClient
) -> None:
    created = ClassroomModelFactory(
        creator=user, building=building, session=session
    ).create_and_refresh()

    updated_input = ClassroomRequestFactory(building=building).update_input()
    update_body = updated_input.model_dump()
    response = client.put(f"{URL_PREFIX}/{created.id}", json=update_body)
    updated = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert updated["name"] == updated_input.name
    assert updated["floor"] == updated_input.floor
    assert updated["capacity"] == updated_input.capacity
    assert updated["audiovisual"] == updated_input.audiovisual


def test_update_classroom_with_restricted_user(
    restricted_user: User,
    building: Building,
    session: Session,
    restricted_client: TestClient,
) -> None:
    created = ClassroomModelFactory(
        creator=restricted_user, building=building, session=session
    ).create_and_refresh()
    GroupModelFactory(session=session).create_and_refresh(
        classrooms=[created], users=[restricted_user]
    )
    updated_input = ClassroomRequestFactory(building=building).update_input()
    update_body = updated_input.model_dump()
    response = restricted_client.put(f"{URL_PREFIX}/{created.id}", json=update_body)
    updated = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert updated["name"] == updated_input.name
    assert updated["floor"] == updated_input.floor
    assert updated["capacity"] == updated_input.capacity
    assert updated["audiovisual"] == updated_input.audiovisual


def test_update_classroom_with_common_user(
    user: User,
    building: Building,
    session: Session,
    common_client: TestClient,
) -> None:
    created = ClassroomModelFactory(
        creator=user, building=building, session=session
    ).create_and_refresh()

    updated_input = ClassroomRequestFactory(building=building).update_input()
    update_body = updated_input.model_dump()
    response = common_client.put(f"{URL_PREFIX}/{created.id}", json=update_body)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_classroom_with_admin_user(
    user: User, building: Building, session: Session, client: TestClient
) -> None:
    created = ClassroomModelFactory(
        creator=user, building=building, session=session
    ).create_and_refresh()

    response = client.delete(f"{URL_PREFIX}/{created.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    with pytest.raises(
        ClassroomNotFound,
    ):
        ClassroomRepository.get_by_id(id=must_be_int(created.id), session=session)


def test_delete_classroom_with_restricted_user(
    restricted_user: User,
    building: Building,
    session: Session,
    restricted_client: TestClient,
) -> None:
    created = ClassroomModelFactory(
        creator=restricted_user, building=building, session=session
    ).create_and_refresh()
    group = GroupModelFactory(session=session).create_and_refresh(
        classrooms=[created], users=[restricted_user]
    )

    response = restricted_client.delete(f"{URL_PREFIX}/{created.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    new_group = GroupRepository.get_by_id(id=must_be_int(group.id), session=session)
    assert len(new_group.classrooms) == 0

    with pytest.raises(
        ClassroomNotFound,
    ):
        ClassroomRepository.get_by_id(id=must_be_int(created.id), session=session)


def test_delete_classroom_with_common_user(
    user: User, building: Building, session: Session, common_client: TestClient
) -> None:
    created = ClassroomModelFactory(
        creator=user, building=building, session=session
    ).create_and_refresh()

    response = common_client.delete(f"{URL_PREFIX}/{created.id}")

    assert response.status_code == status.HTTP_403_FORBIDDEN
