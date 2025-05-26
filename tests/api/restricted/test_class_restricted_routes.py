from fastapi import status
from fastapi.testclient import TestClient

from server.models.database.class_db_model import Class

URL_PREFIX = "/classes"


def test_get_class_by_id_with_admin_user(class_: Class, client: TestClient) -> None:
    response = client.get(f"{URL_PREFIX}/{class_.id}")
    read = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert read["id"] == class_.id
