from datetime import datetime, timedelta

from server.models.database.user_db_model import User
from server.models.database.user_session_db_model import UserSession
from server.models.http.responses.user_session_response import (
    UserSessionResponse,
    get_device_from_user_agent,
)
from tests.utils.academic_test_utils import make_user

_DESKTOP_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
_MOBILE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
)


def _make_session(*, user: User, user_agent: str = _DESKTOP_UA) -> UserSession:
    session = UserSession(
        id="a-session-id",
        user_id=user.id,
        user_agent=user_agent,
        ip_address="127.0.0.1",
        expires_at=datetime(2025, 1, 1) + timedelta(days=30),
        created_at=datetime(2025, 1, 1),
    )
    session.user = user
    return session


class TestGetDeviceFromUserAgent:
    def test_desktop_user_agent_returns_desktop(self) -> None:
        assert get_device_from_user_agent(_DESKTOP_UA) == "Desktop"

    def test_mobile_user_agent_returns_the_device_family(self) -> None:
        device = get_device_from_user_agent(_MOBILE_UA)
        assert device != "Desktop"


class TestUserSessionResponse:
    def test_from_session(self) -> None:
        user = make_user(name="Ana")
        session = _make_session(user=user)

        data = UserSessionResponse.from_session(session)

        assert data.id == "a-session-id"
        assert data.user_id == user.id
        assert data.user_name == "Ana"
        assert data.user_email == user.email
        assert data.device == "Desktop"
        assert data.ip_address == "127.0.0.1"

    def test_from_sessions(self) -> None:
        user = make_user()
        session1 = _make_session(user=user)
        session1.id = "session-1"
        session2 = _make_session(user=user)
        session2.id = "session-2"

        data = UserSessionResponse.from_sessions([session1, session2])

        assert [d.id for d in data] == ["session-1", "session-2"]
