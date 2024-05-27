from fastapi.testclient import TestClient
from sqlmodel import Session

from server.mocks.services.cognito_client_mock import CognitoClientMock
from server.models.database.building_db_model import Building  # noqa
from server.models.database.user_db_model import User  # noqa
from server.models.http.requests.user_request_models import UserRegister
from server.repositories.users_repository import UserRepository


def test_user_get(client: TestClient, user: User, db: Session) -> None:
    """Test user endpoint returns authorized user."""
    my_user = UserRegister(
        email="test@mail.com",
        is_admin=True,
        name="Test",
        username="test_user",
    )
    new_user = UserRepository.create(
        session=db,
        user_in=my_user,
        creator=user,
        cognito_client=CognitoClientMock(),
    )
    resp = client.get("/users")
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == my_user.email
