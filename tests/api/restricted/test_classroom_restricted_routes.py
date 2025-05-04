from fastapi import status
from fastapi.testclient import TestClient

import pytest
from sqlmodel import Session

from server.models.database.user_db_model import User
from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.group_db_model import Group

from server.repositories.classroom_repository import (
    ClassroomNotFound,
    ClassroomRepository,
)
from server.repositories.group_repository import GroupRepository
from server.utils.must_be_int import must_be_int
from tests.factories.model.building_model_factory import BuildingModelFactory
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.model.group_model_factory import GroupModelFactory
from tests.factories.request.classroom_request_factory import ClassroomRequestFactory


URL_PREFIX = "/classrooms"


def test_get_classroom_by_id_with_admin_user(
    classroom: Classroom, client: TestClient
) -> None:
    response = client.get(f"{URL_PREFIX}/{classroom.id}")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["id"] == classroom.id
    assert data["name"] == classroom.name
    assert data["floor"] == classroom.floor
    assert data["capacity"] == classroom.capacity
    assert data["audiovisual"] == classroom.audiovisual


def test_get_classroom_by_id_with_restricted_user(
    classroom: Classroom,
    restricted_client: TestClient,
) -> None:
    response = restricted_client.get(f"{URL_PREFIX}/{classroom.id}")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["id"] == classroom.id
    assert data["name"] == classroom.name
    assert data["floor"] == classroom.floor
    assert data["capacity"] == classroom.capacity
    assert data["audiovisual"] == classroom.audiovisual


def test_get_classroom_by_id_with_restricted_user_outisder_group(
    restricted_user: User,
    building: Building,
    session: Session,
    restricted_client: TestClient,
) -> None:
    insider_group = GroupModelFactory(
        building=building, session=session
    ).create_and_refresh(main=True)
    outsider_group = GroupModelFactory(
        building=building, session=session
    ).create_and_refresh(users=[restricted_user], main=False)

    classroom = ClassroomModelFactory(
        creator=restricted_user, group=insider_group, session=session
    ).create_and_refresh()

    response = restricted_client.get(f"{URL_PREFIX}/{classroom.id}")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert outsider_group.classrooms == []


def test_get_classroom_by_id_with_common_user(
    classroom: Classroom, common_client: TestClient
) -> None:
    response = common_client.get(f"{URL_PREFIX}/{classroom.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_classroom_with_admin_user(
    user: User, group: Group, client: TestClient
) -> None:
    input = ClassroomRequestFactory(group=group).create_input()
    body = input.model_dump()
    response = client.post(URL_PREFIX, json=body)
    created = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert created["name"] == input.name
    assert created["created_by"] == user.name
    assert created["building_id"] == group.building.id


def test_create_classroom_with_restricted_user(
    restricted_user: User,
    group: Group,
    session: Session,
    restricted_client: TestClient,
) -> None:
    input = ClassroomRequestFactory(group=group).create_input()
    body = input.model_dump()

    response = restricted_client.post(URL_PREFIX, json=body)
    created = response.json()

    main_group = GroupRepository.get_by_id(id=must_be_int(group.id), session=session)
    assert len(main_group.classrooms) == 0
    assert main_group.main

    assert response.status_code == status.HTTP_200_OK
    assert created["name"] == input.name
    assert created["created_by"] == restricted_user.name
    assert created["building_id"] == group.building.id


def test_create_classroom_with_restricted_user_outisder_group(
    restricted_user: User,
    building: Building,
    session: Session,
    restricted_client: TestClient,
) -> None:
    insider_group = GroupModelFactory(
        building=building, session=session
    ).create_and_refresh(main=True)
    outsider_group = GroupModelFactory(
        building=building, session=session
    ).create_and_refresh(users=[restricted_user], main=False)

    input = ClassroomRequestFactory(group=insider_group).create_input()
    response = restricted_client.post(URL_PREFIX, json=input.model_dump())
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert outsider_group.classrooms == []
    assert insider_group.classrooms == []


def test_create_classroom_with_group_in_other_building(
    user: User,
    restricted_user: User,
    building: Building,
    session: Session,
    restricted_client: TestClient,
) -> None:
    building_B = BuildingModelFactory(creator=user, session=session).create_and_refresh(
        users=[restricted_user]
    )
    outsider_group = GroupModelFactory(
        building=building_B, session=session
    ).create_and_refresh(users=[restricted_user], main=False)

    input = ClassroomRequestFactory(group=outsider_group).create_input(
        building_id=must_be_int(building.id)
    )
    response = restricted_client.post(URL_PREFIX, json=input.model_dump())
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_classroom_with_user_in_other_building(
    user: User,
    restricted_user: User,
    group: Group,
    session: Session,
    restricted_client: TestClient,
) -> None:
    building_B = BuildingModelFactory(creator=user, session=session).create_and_refresh(
        users=[restricted_user]
    )
    restricted_user.buildings = [building_B]
    session.add(restricted_user)
    session.commit()

    input = ClassroomRequestFactory(group=group).create_input()
    response = restricted_client.post(URL_PREFIX, json=input.model_dump())
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_classroom_with_common_user(
    group: Group, common_client: TestClient
) -> None:
    input = ClassroomRequestFactory(group=group).create_input()
    body = input.model_dump()
    response = common_client.post(URL_PREFIX, json=body)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_classroom_with_admin_user(
    group: Group, classroom: Classroom, session: Session, client: TestClient
) -> None:
    updated_input = ClassroomRequestFactory(group=group).update_input()
    update_body = updated_input.model_dump()
    response = client.put(f"{URL_PREFIX}/{classroom.id}", json=update_body)
    updated = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert updated["name"] == updated_input.name
    assert updated["floor"] == updated_input.floor
    assert updated["capacity"] == updated_input.capacity
    assert updated["audiovisual"] == updated_input.audiovisual


def test_update_classroom_with_restricted_user(
    group: Group,
    classroom: Classroom,
    restricted_client: TestClient,
) -> None:
    updated_input = ClassroomRequestFactory(group=group).update_input()
    update_body = updated_input.model_dump()
    response = restricted_client.put(f"{URL_PREFIX}/{classroom.id}", json=update_body)
    updated = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert updated["name"] == updated_input.name
    assert updated["floor"] == updated_input.floor
    assert updated["capacity"] == updated_input.capacity
    assert updated["audiovisual"] == updated_input.audiovisual


def test_update_classroom_with_restricted_user_outisder_group(
    restricted_user: User,
    building: Building,
    session: Session,
    restricted_client: TestClient,
) -> None:
    insider_group = GroupModelFactory(
        building=building, session=session
    ).create_and_refresh(main=True)
    outsider_group = GroupModelFactory(  # noqa: F841
        building=building, session=session
    ).create_and_refresh(users=[restricted_user], main=False)
    classroom = ClassroomModelFactory(
        creator=restricted_user, group=insider_group, session=session
    ).create_and_refresh()
    updated_input = ClassroomRequestFactory(group=insider_group).update_input()
    update_body = updated_input.model_dump()
    response = restricted_client.put(f"{URL_PREFIX}/{classroom.id}", json=update_body)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_classroom_with_group_in_other_building(
    user: User,
    restricted_user: User,
    building: Building,
    classroom: Classroom,
    session: Session,
    restricted_client: TestClient,
) -> None:
    building_B = BuildingModelFactory(creator=user, session=session).create_and_refresh(
        users=[restricted_user]
    )
    outsider_group = GroupModelFactory(
        building=building_B, session=session
    ).create_and_refresh(users=[restricted_user], main=False)

    input = ClassroomRequestFactory(group=outsider_group).update_input(
        building_id=must_be_int(building.id)
    )
    response = restricted_client.put(
        f"{URL_PREFIX}/{classroom.id}", json=input.model_dump()
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_classroom_with_user_in_other_building(
    user: User,
    restricted_user: User,
    group: Group,
    classroom: Classroom,
    session: Session,
    restricted_client: TestClient,
) -> None:
    building_B = BuildingModelFactory(creator=user, session=session).create_and_refresh(
        users=[restricted_user]
    )
    restricted_user.buildings = [building_B]
    group.users = []
    session.add_all([group, restricted_user])
    session.commit()

    input = ClassroomRequestFactory(group=group).update_input()
    response = restricted_client.put(
        f"{URL_PREFIX}/{classroom.id}", json=input.model_dump()
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_classroom_with_common_user(
    classroom: Classroom,
    group: Group,
    common_client: TestClient,
) -> None:
    updated_input = ClassroomRequestFactory(group=group).update_input()
    update_body = updated_input.model_dump()
    response = common_client.put(f"{URL_PREFIX}/{classroom.id}", json=update_body)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_classroom_with_admin_user(
    user: User, group: Group, session: Session, client: TestClient
) -> None:
    classrooms = ClassroomModelFactory(
        creator=user, group=group, session=session
    ).create_many_default_and_refresh()
    deleted = classrooms[0]
    response = client.delete(f"{URL_PREFIX}/{deleted.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    updated_group = GroupRepository.get_by_id(id=must_be_int(group.id), session=session)
    assert (
        len(updated_group.classrooms)
        == ClassroomModelFactory.CREATE_MANY_DEFAULT_COUNT - 1
    )
    with pytest.raises(
        ClassroomNotFound,
    ):
        ClassroomRepository.get_by_id(id=must_be_int(deleted.id), session=session)


def test_delete_classroom_with_restricted_user(
    restricted_user: User,
    group: Group,
    session: Session,
    restricted_client: TestClient,
) -> None:
    classrooms = ClassroomModelFactory(
        creator=restricted_user, group=group, session=session
    ).create_many_default_and_refresh()
    first = classrooms[0]

    response = restricted_client.delete(f"{URL_PREFIX}/{first.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    new_group = GroupRepository.get_by_id(id=must_be_int(group.id), session=session)
    assert (
        len(new_group.classrooms) == ClassroomModelFactory.CREATE_MANY_DEFAULT_COUNT - 1
    )

    with pytest.raises(
        ClassroomNotFound,
    ):
        ClassroomRepository.get_by_id(id=must_be_int(first.id), session=session)


def test_delete_classroom_with_restricted_user_outisder_group(
    restricted_user: User,
    building: Building,
    session: Session,
    restricted_client: TestClient,
) -> None:
    insider_group = GroupModelFactory(
        building=building, session=session
    ).create_and_refresh(main=True)
    outsider_group = GroupModelFactory(  # noqa: F841
        building=building, session=session
    ).create_and_refresh(users=[restricted_user], main=False)

    classroom = ClassroomModelFactory(
        creator=restricted_user, group=insider_group, session=session
    ).create_and_refresh()
    response = restricted_client.delete(f"{URL_PREFIX}/{classroom.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_classroom_last_one_in_group(
    classroom: Classroom, restricted_client: TestClient
) -> None:
    response = restricted_client.delete(f"{URL_PREFIX}/{classroom.id}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_delete_classroom_with_common_user(
    user: User, group: Group, session: Session, common_client: TestClient
) -> None:
    created = ClassroomModelFactory(
        creator=user, group=group, session=session
    ).create_and_refresh()

    response = common_client.delete(f"{URL_PREFIX}/{created.id}")

    assert response.status_code == status.HTTP_403_FORBIDDEN
