import pytest
from fastapi import status
from httpx import AsyncClient

from server.models.database.classroom_db_model import Classroom
from tests.utils.building_test_utils import get_testing_building
from tests.utils.classroom_test_utils import (
    add_classroom,
    make_classroom_register_input,
)
from tests.utils.default_values.test_classroom_default_values import ClassroomDefaultValues
from tests.utils.user_test_utils import get_test_admin_user

MAX_CLASSROOM_COUNT = 5


@pytest.mark.asyncio
async def test_classroom_get_all(client: AsyncClient) -> None:
    user = await get_test_admin_user()
    building = await get_testing_building()

    for i in range(MAX_CLASSROOM_COUNT):
        await add_classroom(f"{ClassroomDefaultValues.NAME} {i}", building, user)

    response = await client.get("/classrooms")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == MAX_CLASSROOM_COUNT


@pytest.mark.asyncio
async def test_classroom_get(client: AsyncClient) -> None:
    user = await get_test_admin_user()
    building = await get_testing_building()

    classroom_id = await add_classroom(ClassroomDefaultValues.NAME, building, user)

    response = await client.get(f"/classrooms/{classroom_id}")
    data = response.json()

    assert data["_id"] == classroom_id
    assert data["name"] == ClassroomDefaultValues.NAME
    assert data["created_by"]["id"] == str(user.id)
    assert data["building"]["id"] == str(building.id)


@pytest.mark.asyncio
async def test_classroom_create(client: AsyncClient) -> None:
    user = await get_test_admin_user()
    building = await get_testing_building()

    building_id = str(building.id)
    register = make_classroom_register_input(ClassroomDefaultValues.NAME, building_id)
    classroom_input = dict(register)

    response = await client.post("/classrooms", json=classroom_input)
    assert response.status_code == status.HTTP_200_OK

    classroom_id = response.json()
    assert isinstance(classroom_id, str)

    classroom = await Classroom.get(classroom_id, fetch_links=True)
    assert classroom is not None

    if classroom:
        user_id = str(user.id)
        assert str(classroom.building.id) == building_id
        assert str(classroom.created_by.id) == user_id
        assert classroom.name == register.name


@pytest.mark.asyncio
async def test_classroom_update(client: AsyncClient) -> None:
    user = await get_test_admin_user()
    building = await get_testing_building()
    building_id = str(building.id)
    classroom_id = await add_classroom(ClassroomDefaultValues.NAME, building, user)

    register = make_classroom_register_input(
        f"{ClassroomDefaultValues.NAME} Updated", building_id
    )
    classroom_input = dict(register)

    response = await client.patch(f"/classrooms/{classroom_id}", json=classroom_input)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data == classroom_id

    updated_classroom = await Classroom.by_id(classroom_id)
    assert updated_classroom.name == register.name


@pytest.mark.asyncio
async def test_classroom_delete(client: AsyncClient) -> None:
    user = await get_test_admin_user()
    building = await get_testing_building()
    classroom_id = await add_classroom(ClassroomDefaultValues.NAME, building, user)

    response = await client.delete(f"/classrooms/{classroom_id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data == 1

    building_id = str(building.id)
    assert not await Classroom.check_classroom_name_exists(
        building_id, ClassroomDefaultValues.NAME
    )
