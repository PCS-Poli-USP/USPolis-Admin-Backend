
import pytest
from httpx import AsyncClient
from fastapi import status

from tests.utils.user_test_utils import get_test_admin_user
from tests.utils.building_test_utils import make_building, add_building

from server.models.database.building_db_model import Building
from server.models.http.requests.building_request_models import BuildingUpdate, BuildingRegister

MAX_BUILDINGS_COUNT = 5


@pytest.mark.asyncio
async def test_building_get_all(client: AsyncClient) -> None:
    user = await get_test_admin_user()
    building_ids = []
    for i in range(MAX_BUILDINGS_COUNT):
        building_id = await add_building(f"Test Get All {i}", user)
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
    building_input = BuildingRegister(name="Test Create")

    response = await client.post("/buildings", json={"name": "Test Create"})
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    building = await Building.get(data, fetch_links=True)

    assert building.name == building_input.name
    assert str(building.created_by.id) == str(user.id)


@pytest.mark.asyncio
async def test_building_update(client: AsyncClient) -> None:
    user = await get_test_admin_user()
    building_id = await add_building("Test", user)

    building_input = BuildingUpdate(name="Test Update")
    response = await client.patch(f"/buildings/{building_id}", json={"name": "Test Update"})
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data == building_id

    updated_building = await Building.by_id(building_id)
    assert updated_building.name == building_input.name


@pytest.mark.asyncio
async def test_building_delete(client: AsyncClient) -> None:
    user = await get_test_admin_user()
    building_id = await add_building("Test Delete", user)

    response = await client.delete(f"/buildings/{building_id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data == 1

    assert not await Building.check_name_exits("Test Delete")
