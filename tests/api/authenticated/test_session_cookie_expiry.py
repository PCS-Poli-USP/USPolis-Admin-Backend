from datetime import timedelta

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.user_db_model import User
from server.repositories.user_session_repository import UserSessionRepository
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.must_be_int import must_be_int

URL = "/users"


def test_expired_session_cookie_is_rejected(
    public_client: TestClient, user: User, session: Session
) -> None:
    user_session = UserSessionRepository.create_session(
        user_id=must_be_int(user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )
    user_session.expires_at = BrazilDatetime.now_utc() - timedelta(days=1)
    session.add(user_session)
    session.commit()

    response = public_client.get(URL, cookies={"session": user_session.id})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_valid_session_cookie_is_accepted(
    public_client: TestClient, user: User, session: Session
) -> None:
    user_session = UserSessionRepository.create_session(
        user_id=must_be_int(user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )
    session.commit()

    response = public_client.get(URL, cookies={"session": user_session.id})

    assert response.status_code == status.HTTP_200_OK
