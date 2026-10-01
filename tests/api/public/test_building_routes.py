from fastapi import status
from fastapi.testclient import TestClient

from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User

URL_PREFIX = "/buildings"


class TestGetAllBuildings:
    def test_returns_all_buildings(
        self, public_client: TestClient, building: Building, admin_user: User
    ) -> None:
        response = public_client.get(URL_PREFIX)

        assert response.status_code == status.HTTP_200_OK
        matches = [b for b in response.json() if b["id"] == building.id]
        assert len(matches) == 1
        assert matches[0]["name"] == building.name
        assert matches[0]["created_by"] == admin_user.name
