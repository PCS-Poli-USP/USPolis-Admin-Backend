from fastapi.testclient import TestClient

from server.models.database.user_db_model import User
from server.models.database.building_db_model import Building

from tests.factories.request.classroom_request_factory import ClassroomRequestFactory


URL_PREFIX = "/classrooms"


def test_create_classroom(user: User, building: Building, client: TestClient) -> None:
    input = ClassroomRequestFactory(building=building).create_input()
    body = input.model_dump()
    response = client.post(URL_PREFIX, json=body)
    created = response.json()

    assert response.status_code == 200
    assert created["name"] == input.name
    assert created["created_by"] == user.name
    assert created["building_id"] == building.id
