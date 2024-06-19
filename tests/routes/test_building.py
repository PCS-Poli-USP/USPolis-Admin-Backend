from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User
from server.models.http.requests.building_request_models import (
    BuildingRegister,
    BuildingUpdate,
)
from server.repositories.building_repository import BuildingRepository
from tests.utils.building_test_utils import (
    add_building,
    check_name_exists,
    make_building,
)
from tests.utils.default_values.test_building_default_values import (
    BuildingDefaultValues,
)

MAX_BUILDINGS_COUNT = 5


def test_building_get_all(db: Session, client: TestClient, user: User) -> None:
    building_ids = []
    for i in range(MAX_BUILDINGS_COUNT):
        building_id = add_building(db, f"{BuildingDefaultValues.NAME} {i}", user)
        building_ids.append(building_id)

    response = client.get("/buildings")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == MAX_BUILDINGS_COUNT


def test_building_get(db: Session, client: TestClient, user: User) -> None:
    building = make_building("Test Get", user)
    db.add(building)
    db.commit()

    building_id = str(building.id)
    response = client.get(f"/buildings/{building_id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == building.name


def test_building_create(db: Session, client: TestClient, user: User) -> None:
    building_input = BuildingRegister(name=BuildingDefaultValues.NAME)

    response = client.post("/admin/buildings", json={"name": BuildingDefaultValues.NAME})
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    id = data["id"]
    building = db.get(Building, id)
    assert building is not None

    if building:
        assert building.name == building_input.name
        assert isinstance(building.created_by, User)
        assert building.created_by.id == user.id


def test_building_update(db: Session, client: TestClient, user: User) -> None:
    building_id = add_building(db, BuildingDefaultValues.NAME, user)

    building_input = BuildingUpdate(name=f"{BuildingDefaultValues.NAME} Updated")
    response = client.put(
        f"/admin/buildings/{building_id}", json={"name": building_input.name}
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == building_id

    updated_building = BuildingRepository.get_by_id(id=building_id, session=db)
    assert updated_building.name == building_input.name


def test_building_delete(db: Session, client: TestClient, user: User) -> None:
    building_id = add_building(db, BuildingDefaultValues.NAME, user)

    response = client.delete(f"/admin/buildings/{building_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not check_name_exists(db, BuildingDefaultValues.NAME)
