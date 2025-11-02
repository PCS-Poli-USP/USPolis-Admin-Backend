from httpx import Response
from server.models.database.building_db_model import Building


class BuildingResponseAsserts:
    @staticmethod
    def assert_building_response(
        response: Response,
        building: Building,
    ) -> None:
        """Assert that the response contains the expected data for a building response based on the building model."""
        data = response.json()
        assert data["id"] == building.id
        assert data["name"] == building.name
