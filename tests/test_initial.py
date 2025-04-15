from fastapi.testclient import TestClient
from sqlmodel import Session


def test_enviroment(client: TestClient, session: Session) -> None:
    """Test if the environment is set up correctly."""
    assert client is not None
    assert session is not None
