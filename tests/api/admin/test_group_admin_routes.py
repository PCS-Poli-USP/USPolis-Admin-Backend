from fastapi.testclient import TestClient
from server.models.database.user_db_model import User

URL_PREFIX = "/admin/groups"


def test_create_group(user: User, client: TestClient) -> None:
    pass
