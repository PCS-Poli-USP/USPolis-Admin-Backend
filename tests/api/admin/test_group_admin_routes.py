from fastapi import status
from fastapi.testclient import TestClient

import pytest
from sqlmodel import Session
from server.repositories.group_repository import GroupNotFound, GroupRepository
from server.repositories.user_repository import UserRepository
from server.utils.must_be_int import must_be_int
from tests.factories.model.building_model_factory import BuildingModelFactory
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.model.group_model_factory import GroupModelFactory
from tests.factories.model.user_model_factory import UserModelFactory
from tests.factories.request.group_request_factory import GroupRequestFactory
from server.models.database.user_db_model import User
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


def test_create_group_with_admin_user(
    user: User, building: Building, session: Session, client: TestClient
) -> None:
    classrooms = ClassroomModelFactory(
        creator=user, building=building, session=session
    ).create_many_default_and_refresh()
    input = GroupRequestFactory(building).create_input(
        classroom_ids=[must_be_int(classrooms[0].id)]
    )
    response = client.post(URL_PREFIX, json=input.model_dump())
    assert response.status_code == status.HTTP_201_CREATED


def test_create_group_with_same_name(
    user: User, building: Building, group: Group, session: Session, client: TestClient
) -> None:
    classrooms = ClassroomModelFactory(
        creator=user, building=building, session=session
    ).create_many_default_and_refresh()
    input = GroupRequestFactory(building).create_input(
        name=group.name, classroom_ids=[must_be_int(classrooms[0].id)]
    )
    response = client.post(f"{URL_PREFIX}", json=input.model_dump())
    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_group_with_users(
    building: Building, group: Group, session: Session, client: TestClient
) -> None:
    user = UserModelFactory(session).create_and_refresh(
        buildings=[building], groups=[group]
    )
    classrooms = ClassroomModelFactory(
        creator=user, building=building, session=session
    ).create_many_default_and_refresh()
    input = GroupRequestFactory(building).create_input(
        user_ids=[must_be_int(user.id)], classroom_ids=[must_be_int(classrooms[0].id)]
    )
    response = client.post(URL_PREFIX, json=input.model_dump())
    assert response.status_code == status.HTTP_201_CREATED

    user = UserRepository.get_by_id(user_id=must_be_int(user.id), session=session)
    user_groups = user.groups
    user_groups_names = [g.name for g in user_groups]
    assert len(user_groups) == 2
    assert input.name in user_groups_names
    assert group.name in user_groups_names


def test_create_group_with_classrooms(
    user: User,
    group: Group,
    building: Building,
    session: Session,
    client: TestClient,
) -> None:
    classrooms = ClassroomModelFactory(
        creator=user, building=building, session=session
    ).create_many_default_and_refresh(count=10)
    ids = []
    for i in range(5):
        ids.append(must_be_int(classrooms[i].id))
    input = GroupRequestFactory(building).create_input(classroom_ids=ids)
    response = client.post(URL_PREFIX, json=input.model_dump())

    assert response.status_code == status.HTTP_201_CREATED


def test_create_group_with_all_classrooms(
    building: Building,
    group: Group,
    session: Session,
    user: User,
    client: TestClient,
) -> None:
    classrooms = ClassroomModelFactory(
        creator=user, building=building, session=session
    ).create_many_default_and_refresh()
    input = GroupRequestFactory(building).create_input(
        classroom_ids=[must_be_int(classroom.id) for classroom in classrooms],
    )
    response = client.post(URL_PREFIX, json=input.model_dump())
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_group_without_classrooms(
    building: Building,
    client: TestClient,
) -> None:
    input = GroupRequestFactory(building).create_input()
    response = client.post(URL_PREFIX, json=input.model_dump())
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_group_with_classrooms_in_other_building(
    user: User,
    building: Building,
    session: Session,
    client: TestClient,
) -> None:
    building_B = BuildingModelFactory(
        creator=user, session=session
    ).create_and_refresh()
    main_group_B = GroupModelFactory(  # noqa: F841
        building=building_B, session=session
    ).create_and_refresh()
    classrooms = ClassroomModelFactory(
        creator=user, building=building_B, session=session
    ).create_many_default_and_refresh(count=5)
    ids = [must_be_int(classroom.id) for classroom in classrooms]
    input = GroupRequestFactory(building).create_input(classroom_ids=ids)
    response = client.post(URL_PREFIX, json=input.model_dump())
    assert response.status_code == status.HTTP_400_BAD_REQUEST


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
    building: Building, user: User, session: Session, client: TestClient
) -> None:
    classrooms = ClassroomModelFactory(
        session=session, creator=user, building=building, group=building.main_group
    ).create_many_default_and_refresh()

    group = GroupModelFactory(building=building, session=session).create_and_refresh(
        classrooms=[classrooms[0]]
    )
    input = GroupRequestFactory(building).update_input(
        classroom_ids=[must_be_int(classrooms[0].id)]
    )
    response = client.put(f"{URL_PREFIX}/{group.id}", json=input.model_dump())
    updated = GroupRepository.get_by_id(
        id=must_be_int(group.id),
        session=session,
    )

    assert response.status_code == status.HTTP_200_OK
    assert updated.name == input.name
    assert len(updated.classrooms) == 1
    assert updated.classrooms[0].id == classrooms[0].id


def test_update_group_with_same_name(
    user: User, building: Building, group: Group, session: Session, client: TestClient
) -> None:
    classrooms = ClassroomModelFactory(
        creator=user, building=building, session=session
    ).create_many_default_and_refresh()
    group_B = GroupModelFactory(building=building, session=session).create_and_refresh(
        classrooms=[classrooms[0]]
    )
    input = GroupRequestFactory(building).update_input(
        name=group.name, classroom_ids=[must_be_int(classrooms[0].id)]
    )
    response = client.put(f"{URL_PREFIX}/{group_B.id}", json=input.model_dump())
    assert response.status_code == status.HTTP_409_CONFLICT


def test_update_group_add_users_without_buildings(
    building: Building, session: Session, client: TestClient
) -> None:
    users = UserModelFactory(session).create_many_default_and_refresh()
    ids = [must_be_int(created.id) for created in users]
    group = GroupModelFactory(building=building, session=session).create_and_refresh()
    input = GroupRequestFactory(building).update_input(user_ids=ids)
    response = client.put(f"{URL_PREFIX}/{group.id}", json=input.model_dump())

    assert response.status_code == status.HTTP_200_OK

    updated = GroupRepository.get_by_id(
        id=must_be_int(group.id),
        session=session,
    )
    assert updated.name == input.name
    assert updated.users is not None
    assert len(updated.users) == UserModelFactory.CREATE_MANY_DEFAULT_COUNT

    updated_users = UserRepository.get_by_ids(
        ids=ids,
        session=session,
    )
    for user in updated_users:
        assert len(user.groups) == 1
        assert user.groups[0].name == input.name
        assert user.buildings is not None
        assert len(user.buildings) == 1


def test_update_group_add_users_with_buildings(
    user: User, building: Building, session: Session, client: TestClient
) -> None:
    building_B = BuildingModelFactory(
        creator=user, session=session
    ).create_and_refresh()
    users = UserModelFactory(session).create_many_and_refresh(buildings=[building_B])
    ids = [must_be_int(created.id) for created in users]
    group = GroupModelFactory(building=building, session=session).create_and_refresh()
    input = GroupRequestFactory(building).update_input(user_ids=ids)
    response = client.put(f"{URL_PREFIX}/{group.id}", json=input.model_dump())

    assert response.status_code == status.HTTP_200_OK

    updated = GroupRepository.get_by_id(
        id=must_be_int(group.id),
        session=session,
    )
    assert updated.name == input.name
    assert updated.users is not None
    assert len(updated.users) == UserModelFactory.CREATE_MANY_DEFAULT_COUNT

    updated_users = UserRepository.get_by_ids(
        ids=ids,
        session=session,
    )
    for user in updated_users:
        assert len(user.groups) == 1
        assert user.groups[0].name == input.name
        assert user.buildings is not None
        assert len(user.buildings) == 2


def test_update_group_remove_users_with_one_group_on_same_building(
    user: User, building: Building, session: Session, client: TestClient
) -> None:
    users = UserModelFactory(session).create_many_and_refresh(buildings=[building])
    ids = [must_be_int(created.id) for created in users]
    group = GroupModelFactory(building=building, session=session).create_and_refresh(
        users=users
    )
    input = GroupRequestFactory(building).update_input(user_ids=[])
    response = client.put(f"{URL_PREFIX}/{group.id}", json=input.model_dump())

    assert response.status_code == status.HTTP_200_OK

    updated = GroupRepository.get_by_id(
        id=must_be_int(group.id),
        session=session,
    )
    assert updated.name == input.name
    assert len(updated.users) == 0

    updated_users = UserRepository.get_by_ids(
        ids=ids,
        session=session,
    )
    for user in updated_users:
        assert len(user.groups) == 0
        assert user.buildings == []


def test_update_group_remove_users_with_groups_on_same_building(
    user: User, group: Group, building: Building, session: Session, client: TestClient
) -> None:
    users = UserModelFactory(session).create_many_and_refresh(
        buildings=[building], groups=[group]
    )
    classrooms = ClassroomModelFactory(
        creator=user, building=building, session=session
    ).create_many_and_refresh()
    selected = []
    selected_ids = []
    for i in range(3):
        selected.append(classrooms[i])
        selected_ids.append(must_be_int(classrooms[i].id))

    ids = [must_be_int(created.id) for created in users]
    group_B = GroupModelFactory(building=building, session=session).create_and_refresh(
        users=users,
        classrooms=selected,
    )
    input = GroupRequestFactory(building).update_input(
        user_ids=[],
        classroom_ids=selected_ids,
    )
    response = client.put(f"{URL_PREFIX}/{group_B.id}", json=input.model_dump())
    assert response.status_code == status.HTTP_200_OK

    updated = GroupRepository.get_by_id(
        id=must_be_int(group_B.id),
        session=session,
    )
    assert updated.name == input.name
    assert len(updated.users) == 0

    updated_users = UserRepository.get_by_ids(
        ids=ids,
        session=session,
    )
    for u in updated_users:
        assert len(u.groups) == 1
        assert u.buildings is not None
        assert len(u.buildings) == 1
        assert u.buildings[0] == building


def test_update_group_remove_users_with_groups_on_diff_buildings(
    user: User, group: Group, building: Building, session: Session, client: TestClient
) -> None:
    building_B = BuildingModelFactory(
        creator=user, session=session
    ).create_and_refresh()
    group_B = GroupModelFactory(
        building=building_B, session=session
    ).create_and_refresh()
    users = UserModelFactory(session).create_many_and_refresh(
        buildings=[building, building_B], groups=[group, group_B]
    )
    ids = [must_be_int(created.id) for created in users]

    input = GroupRequestFactory(building).update_input(
        user_ids=[],
    )
    response = client.put(f"{URL_PREFIX}/{group.id}", json=input.model_dump())
    assert response.status_code == status.HTTP_200_OK

    updated = GroupRepository.get_by_id(
        id=must_be_int(group.id),
        session=session,
    )
    assert updated.name == input.name
    assert len(updated.users) == 0

    updated_users = UserRepository.get_by_ids(
        ids=ids,
        session=session,
    )
    for u in updated_users:
        assert len(u.groups) == 1
        assert u.buildings is not None
        assert len(u.buildings) == 1
        assert u.buildings[0] == building_B


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
