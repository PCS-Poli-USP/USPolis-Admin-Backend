from datetime import timedelta

from sqlmodel import Session

from server.models.database.user_db_model import User
from server.repositories.user_session_repository import (
    SESSION_DURATION_DAYS,
    SESSION_MAX_AGE_DAYS,
    UserSessionRepository,
)
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.must_be_int import must_be_int
from tests.factories.model.user_model_factory import UserModelFactory


def test_create_session_sets_expiry_within_sliding_window(
    user: User, session: Session
) -> None:
    user_session = UserSessionRepository.create_session(
        user_id=must_be_int(user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )

    expected = user_session.created_at + timedelta(days=SESSION_DURATION_DAYS)
    assert abs((user_session.expires_at - expected).total_seconds()) < 5


def test_extend_session_pushes_expiry_forward(user: User, session: Session) -> None:
    user_session = UserSessionRepository.create_session(
        user_id=must_be_int(user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )
    user_session.expires_at = BrazilDatetime.now_utc()
    session.add(user_session)
    session.commit()

    UserSessionRepository.extend_session(user_session=user_session, session=session)

    assert user_session.expires_at > BrazilDatetime.now_utc() + timedelta(days=29)


def test_extend_session_never_pushes_expiry_past_max_age(
    user: User, session: Session
) -> None:
    user_session = UserSessionRepository.create_session(
        user_id=must_be_int(user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )
    user_session.created_at = BrazilDatetime.now_utc() - timedelta(
        days=SESSION_MAX_AGE_DAYS - 1
    )
    session.add(user_session)
    session.commit()

    UserSessionRepository.extend_session(user_session=user_session, session=session)

    hard_cap = user_session.created_at + timedelta(days=SESSION_MAX_AGE_DAYS)
    assert user_session.expires_at == hard_cap


def test_has_reached_max_age(user: User, session: Session) -> None:
    fresh_session = UserSessionRepository.create_session(
        user_id=must_be_int(user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )
    assert UserSessionRepository.has_reached_max_age(user_session=fresh_session) is False

    fresh_session.created_at = BrazilDatetime.now_utc() - timedelta(
        days=SESSION_MAX_AGE_DAYS + 1
    )
    assert UserSessionRepository.has_reached_max_age(user_session=fresh_session) is True


def test_start_or_renew_session_reuses_a_session_within_max_age(
    user: User, session: Session
) -> None:
    original = UserSessionRepository.create_session(
        user_id=must_be_int(user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )
    session.commit()

    renewed = UserSessionRepository.start_or_renew_session(
        user_id=must_be_int(user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )

    assert renewed.id == original.id


def test_start_or_renew_session_replaces_a_session_past_max_age(
    user: User, session: Session
) -> None:
    original = UserSessionRepository.create_session(
        user_id=must_be_int(user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )
    original.created_at = BrazilDatetime.now_utc() - timedelta(
        days=SESSION_MAX_AGE_DAYS + 1
    )
    session.add(original)
    session.commit()
    original_id = original.id

    renewed = UserSessionRepository.start_or_renew_session(
        user_id=must_be_int(user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )
    session.commit()

    assert renewed.id != original_id
    assert UserSessionRepository.has_reached_max_age(user_session=renewed) is False
    assert UserSessionRepository.get_session_opt(id=original_id, session=session) is None


def test_start_or_renew_session_reuses_a_session_when_ip_address_changes(
    user: User, session: Session
) -> None:
    original = UserSessionRepository.create_session(
        user_id=must_be_int(user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )
    session.commit()

    renewed = UserSessionRepository.start_or_renew_session(
        user_id=must_be_int(user.id),
        user_agent="pytest",
        ip_address="10.0.0.99",
        session=session,
    )

    assert renewed.id == original.id


def test_get_valid_session_for_renewal_returns_matching_session(
    user: User, session: Session
) -> None:
    user_session = UserSessionRepository.create_session(
        user_id=must_be_int(user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )
    session.commit()

    result = UserSessionRepository.get_valid_session_for_renewal(
        session_id=user_session.id, user_id=must_be_int(user.id), session=session
    )

    assert result is not None
    assert result.id == user_session.id


def test_get_valid_session_for_renewal_returns_none_for_unknown_id(
    session: Session,
) -> None:
    result = UserSessionRepository.get_valid_session_for_renewal(
        session_id="does-not-exist", user_id=1, session=session
    )

    assert result is None


def test_get_valid_session_for_renewal_returns_none_for_different_user(
    user: User, session: Session
) -> None:
    other_user = UserModelFactory(session).create_and_refresh()
    user_session = UserSessionRepository.create_session(
        user_id=must_be_int(user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )
    session.commit()

    result = UserSessionRepository.get_valid_session_for_renewal(
        session_id=user_session.id,
        user_id=must_be_int(other_user.id),
        session=session,
    )

    assert result is None


def test_get_valid_session_for_renewal_returns_none_for_expired_session(
    user: User, session: Session
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

    result = UserSessionRepository.get_valid_session_for_renewal(
        session_id=user_session.id, user_id=must_be_int(user.id), session=session
    )

    assert result is None


def test_get_valid_session_for_renewal_deletes_session_past_max_age(
    user: User, session: Session
) -> None:
    user_session = UserSessionRepository.create_session(
        user_id=must_be_int(user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )
    user_session.created_at = BrazilDatetime.now_utc() - timedelta(
        days=SESSION_MAX_AGE_DAYS + 1
    )
    session.add(user_session)
    session.commit()
    session_id = user_session.id

    result = UserSessionRepository.get_valid_session_for_renewal(
        session_id=session_id, user_id=must_be_int(user.id), session=session
    )
    session.commit()

    assert result is None
    assert UserSessionRepository.get_session_opt(id=session_id, session=session) is None
