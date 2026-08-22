from datetime import timedelta

from server.models.database.user_session_db_model import UserSession
from server.utils.brazil_datetime import BrazilDatetime


def make_session(*, expires_at_delta: timedelta) -> UserSession:
    return UserSession(
        user_id=1,
        user_agent="pytest",
        ip_address="127.0.0.1",
        expires_at=BrazilDatetime.now_utc() + expires_at_delta,
    )


def test_is_expired_false_for_future_expiry() -> None:
    user_session = make_session(expires_at_delta=timedelta(days=1))
    assert user_session.is_expired() is False


def test_is_expired_true_for_past_expiry() -> None:
    user_session = make_session(expires_at_delta=timedelta(days=-1))
    assert user_session.is_expired() is True
