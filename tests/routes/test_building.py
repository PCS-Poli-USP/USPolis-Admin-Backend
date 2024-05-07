import pytest
from fastapi import status
from httpx import AsyncClient

from server.models.database.building_db_model import Building
from server.models.http.requests.building_request_models import (
    BuildingRegister,
    BuildingUpdate,
)
from tests.utils.building_test_utils import add_building, make_building
from tests.utils.default_values.test_building_default_values import (
    BuildingDefaultValues,
)
from tests.utils.user_test_utils import get_test_admin_user

MAX_BUILDINGS_COUNT = 5


@pytest.mark.asyncio
async def test_building_get_all(client: AsyncClient) -> None:
    user = await get_test_admin_user()
    building_ids = []
    for i in range(MAX_BUILDINGS_COUNT):
        building_id = await add_building(f"{BuildingDefaultValues.NAME} {i}", user)
        building_ids.append(building_id)

    response = await client.get("/buildings")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == MAX_BUILDINGS_COUNT


@pytest.mark.asyncio
async def test_building_get(client: AsyncClient) -> None:
    user = await get_test_admin_user()
    building = make_building("Test Get", user)
    await building.create()

    building_id = str(building.id)
    response = await client.get(f"/buildings/{building_id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == building.name

    user_id = str(user.id)
    assert data["created_by"]["id"] == user_id


@pytest.mark.asyncio
async def test_building_create(client: AsyncClient) -> None:
    user = await get_test_admin_user()
    building_input = BuildingRegister(name=BuildingDefaultValues.NAME)

    response = await client.post(
        "/buildings", json={"name": BuildingDefaultValues.NAME}
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    building = await Building.get(data, fetch_links=True)
    assert building is not None

    if building:
        assert building.name == building_input.name
        assert str(building.created_by.id) == str(user.id)


@pytest.mark.asyncio
async def test_building_update(client: AsyncClient) -> None:
    user = await get_test_admin_user()
    building_id = await add_building(BuildingDefaultValues.NAME, user)

    building_input = BuildingUpdate(name=f"{BuildingDefaultValues.NAME} Updated")
    response = await client.patch(
        f"/buildings/{building_id}", json={"name": building_input.name}
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, str)
    assert data == building_id

    updated_building = await Building.by_id(building_id)
    assert updated_building.name == building_input.name


@pytest.mark.asyncio
async def test_building_delete(client: AsyncClient) -> None:
    user = await get_test_admin_user()
    building_id = await add_building(BuildingDefaultValues.NAME, user)

    response = await client.delete(f"/buildings/{building_id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data == 1

    assert not await Building.check_name_exits(BuildingDefaultValues.NAME)
