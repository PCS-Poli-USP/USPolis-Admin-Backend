import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from sqlalchemy.exc import NoResultFound

from server.models.database.user_db_model import User
from server.models.database.building_db_model import Building
from server.repositories.user_repository import UserRepository
from server.utils.must_be_int import must_be_int
from tests.factories.model.group_model_factory import GroupModelFactory
from tests.factories.model.user_model_factory import UserModelFactory
from tests.factories.request.user_request_factory import UserRequestFactory


URL_PREFIX = "/admin/users"


def test_create_user_with_admin_user(client: TestClient) -> None:
    input = UserRequestFactory().create_input()
    body = input.model_dump()
    response = client.post(URL_PREFIX, json=body)
    created = response.json()

    assert response.status_code == 200
    assert created["email"] == input.email
    assert created["name"] == input.name
    assert created["is_admin"] == input.is_admin
    assert created["buildings"] is None


def test_get_all_users_with_admin_user(client: TestClient, session: Session) -> None:
    factory = UserModelFactory(session)
    users = factory.create_many_default()
    factory.commit()
    factory.refresh_many(users)

    response = client.get(URL_PREFIX)
    assert response.status_code == 200

    query_users = response.json()
    assert len(query_users) == len(users) + 1
    ids = [user["id"] for user in query_users]
    for user in users:
        assert user.id in ids


def test_update_user_to_admin_with_admin_user(
    client: TestClient, session: Session
) -> None:
    factory = UserModelFactory(session)
    user = factory.create_and_refresh()
    input = UserRequestFactory().update_input(is_admin=True)
    response = client.put(f"{URL_PREFIX}/{user.id}", json=input.model_dump())

    assert response.status_code == 200
    updated = response.json()
    assert updated["id"] == user.id
    assert updated["is_admin"] is True


def test_update_self_admin_status_with_admin_user(
    user: User,
    client: TestClient,
) -> None:
    input = UserRequestFactory().update_input(group_ids=[], is_admin=False)
    response = client.put(f"{URL_PREFIX}/{user.id}", json=input.model_dump())
    assert response.status_code == 400


def test_update_user_buildings_with_admin_user(
    client: TestClient, session: Session, building: Building
) -> None:
    group_factory = GroupModelFactory(building=building, session=session)
    group = group_factory.create_and_refresh()
    factory = UserModelFactory(session)
    user = factory.create_and_refresh()

    input = UserRequestFactory().update_input(group_ids=[must_be_int(group.id)])

    response = client.put(
        f"{URL_PREFIX}/{user.id}",
        json=input.model_dump(),
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["id"] == user.id
    assert updated["buildings"] is not None


def test_update_user_to_admin_and_groups_with_admin_user(
    client: TestClient, session: Session, building: Building
) -> None:
    factory = UserModelFactory(session)
    user = factory.create_and_refresh()

    group_factory = GroupModelFactory(building=building, session=session)
    group = group_factory.create_and_refresh()

    input = UserRequestFactory().update_input(
        is_admin=True, group_ids=[must_be_int(group.id)]
    )

    response = client.put(
        f"{URL_PREFIX}/{user.id}",
        json=input.model_dump(),
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["id"] == user.id
    assert updated["is_admin"] is True

    assert len(updated["buildings"]) == 1
    new_building = updated["buildings"][0]
    assert new_building["id"] == building.id
    assert new_building["name"] == building.name

    assert len(updated["groups"]) == 1
    new_group = updated["groups"][0]
    assert new_group["id"] == group.id
    assert new_group["name"] == group.name


def test_delete_user_with_admin_user(client: TestClient, session: Session) -> None:
    factory = UserModelFactory(session)
    user = factory.create_and_refresh()

    response = client.delete(f"{URL_PREFIX}/{user.id}")
    assert response.status_code == 204

    with pytest.raises(
        NoResultFound,
    ):
        UserRepository.get_by_id(user_id=must_be_int(user.id), session=session)


def test_delete_self_with_admin_user(user: User, client: TestClient) -> None:
    response = client.delete(f"{URL_PREFIX}/{user.id}")
    assert response.status_code == 400
