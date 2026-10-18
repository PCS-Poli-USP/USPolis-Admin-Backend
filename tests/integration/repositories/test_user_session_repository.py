from datetime import timedelta

from sqlmodel import Session

from server.models.database.user_db_model import User
from server.models.database.user_session_db_model import UserSession
from server.repositories.user_session_repository import (
    SESSION_DURATION_DAYS,
    SESSION_MAX_AGE_DAYS,
    UserSessionRepository,
    hash_session_token,
)
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.must_be_int import must_be_int
from tests.factories.model.user_model_factory import UserModelFactory


def test_create_session_sets_expiry_within_sliding_window(
    admin_user: User, session: Session
) -> None:
    user_session, token = UserSessionRepository.create_session(
        user_id=must_be_int(admin_user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )

    expected = user_session.created_at + timedelta(days=SESSION_DURATION_DAYS)
    assert abs((user_session.expires_at - expected).total_seconds()) < 5


def test_extend_session_pushes_expiry_forward(
    admin_user: User, session: Session
) -> None:
    user_session, token = UserSessionRepository.create_session(
        user_id=must_be_int(admin_user.id),
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
    admin_user: User, session: Session
) -> None:
    user_session, token = UserSessionRepository.create_session(
        user_id=must_be_int(admin_user.id),
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


def test_has_reached_max_age(admin_user: User, session: Session) -> None:
    fresh_session, token = UserSessionRepository.create_session(
        user_id=must_be_int(admin_user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )
    assert (
        UserSessionRepository.has_reached_max_age(user_session=fresh_session) is False
    )

    fresh_session.created_at = BrazilDatetime.now_utc() - timedelta(
        days=SESSION_MAX_AGE_DAYS + 1
    )
    assert UserSessionRepository.has_reached_max_age(user_session=fresh_session) is True


def test_start_or_renew_session_reuses_a_session_within_max_age(
    admin_user: User, session: Session
) -> None:
    original, token = UserSessionRepository.create_session(
        user_id=must_be_int(admin_user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )
    session.commit()

    renewed, _ = UserSessionRepository.start_or_renew_session(
        user_id=must_be_int(admin_user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )

    assert renewed.id == original.id


def test_start_or_renew_session_replaces_a_session_past_max_age(
    admin_user: User, session: Session
) -> None:
    original, token = UserSessionRepository.create_session(
        user_id=must_be_int(admin_user.id),
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

    renewed, _ = UserSessionRepository.start_or_renew_session(
        user_id=must_be_int(admin_user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )
    session.commit()

    assert renewed.id != original_id
    assert UserSessionRepository.has_reached_max_age(user_session=renewed) is False
    assert (
        UserSessionRepository.get_session_opt(id=original_id, session=session) is None
    )


def test_start_or_renew_session_reuses_a_session_when_ip_address_changes(
    admin_user: User, session: Session
) -> None:
    original, token = UserSessionRepository.create_session(
        user_id=must_be_int(admin_user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )
    session.commit()

    renewed, _ = UserSessionRepository.start_or_renew_session(
        user_id=must_be_int(admin_user.id),
        user_agent="pytest",
        ip_address="10.0.0.99",
        session=session,
    )

    assert renewed.id == original.id


def test_get_valid_session_for_renewal_returns_matching_session(
    admin_user: User, session: Session
) -> None:
    user_session, token = UserSessionRepository.create_session(
        user_id=must_be_int(admin_user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )
    session.commit()

    result = UserSessionRepository.get_valid_session_for_renewal(
        token=token, user_id=must_be_int(admin_user.id), session=session
    )

    assert result is not None
    assert result.id == user_session.id


def test_get_valid_session_for_renewal_returns_none_for_unknown_id(
    session: Session,
) -> None:
    result = UserSessionRepository.get_valid_session_for_renewal(
        token="does-not-exist", user_id=1, session=session
    )

    assert result is None


def test_get_valid_session_for_renewal_returns_none_for_different_user(
    admin_user: User, session: Session
) -> None:
    other_user = UserModelFactory(session).create_and_refresh()
    user_session, token = UserSessionRepository.create_session(
        user_id=must_be_int(admin_user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )
    session.commit()

    result = UserSessionRepository.get_valid_session_for_renewal(
        token=token,
        user_id=must_be_int(other_user.id),
        session=session,
    )

    assert result is None


def test_get_valid_session_for_renewal_returns_none_for_expired_session(
    admin_user: User, session: Session
) -> None:
    user_session, token = UserSessionRepository.create_session(
        user_id=must_be_int(admin_user.id),
        user_agent="pytest",
        ip_address="127.0.0.1",
        session=session,
    )
    user_session.expires_at = BrazilDatetime.now_utc() - timedelta(days=1)
    session.add(user_session)
    session.commit()

    result = UserSessionRepository.get_valid_session_for_renewal(
        token=token, user_id=must_be_int(admin_user.id), session=session
    )

    assert result is None


def test_get_valid_session_for_renewal_deletes_session_past_max_age(
    admin_user: User, session: Session
) -> None:
    user_session, token = UserSessionRepository.create_session(
        user_id=must_be_int(admin_user.id),
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
        token=token, user_id=must_be_int(admin_user.id), session=session
    )
    session.commit()

    assert result is None
    assert UserSessionRepository.get_session_opt(id=session_id, session=session) is None


class TestSessionTokens:
    """The cookie token is never stored, only its SHA-256 (security item 8)."""

    def test_only_the_hash_of_the_token_is_stored(
        self, admin_user: User, session: Session
    ) -> None:
        user_session, token = UserSessionRepository.create_session(
            user_id=must_be_int(admin_user.id),
            user_agent="pytest",
            ip_address="127.0.0.1",
            session=session,
        )
        session.commit()

        assert user_session.token_hash == hash_session_token(token)
        assert token not in (user_session.id, user_session.token_hash)

    def test_finds_the_session_by_its_token(
        self, admin_user: User, session: Session
    ) -> None:
        user_session, token = UserSessionRepository.create_session(
            user_id=must_be_int(admin_user.id),
            user_agent="pytest",
            ip_address="127.0.0.1",
            session=session,
        )
        session.commit()

        found = UserSessionRepository.get_by_token_opt(token=token, session=session)
        assert found is not None
        assert found.id == user_session.id
        # The id is no longer a credential.
        assert (
            UserSessionRepository.get_by_token_opt(
                token=user_session.id, session=session
            )
            is None
        )

    def test_legacy_cookie_still_resolves_after_the_backfill(
        self, admin_user: User, session: Session
    ) -> None:
        """Rows from before the migration: cookie == id, token_hash = sha256(id)."""
        legacy_id = "0f" * 16
        legacy = UserSession(
            id=legacy_id,
            user_id=must_be_int(admin_user.id),
            user_agent="pytest",
            ip_address="127.0.0.1",
            expires_at=BrazilDatetime.now_utc() + timedelta(days=1),
            token_hash=hash_session_token(legacy_id),
        )
        session.add(legacy)
        session.commit()

        found = UserSessionRepository.get_by_token_opt(token=legacy_id, session=session)
        assert found is not None
        assert found.id == legacy_id

    def test_rotate_token_invalidates_the_previous_one(
        self, admin_user: User, session: Session
    ) -> None:
        user_session, old_token = UserSessionRepository.create_session(
            user_id=must_be_int(admin_user.id),
            user_agent="pytest",
            ip_address="127.0.0.1",
            session=session,
        )
        session.commit()

        new_token = UserSessionRepository.rotate_token(
            user_session=user_session, session=session
        )
        session.commit()

        assert new_token != old_token
        assert (
            UserSessionRepository.get_by_token_opt(token=old_token, session=session)
            is None
        )
        assert (
            UserSessionRepository.get_by_token_opt(token=new_token, session=session)
            is not None
        )

    def test_renewing_at_login_issues_a_new_token(
        self, admin_user: User, session: Session
    ) -> None:
        original, old_token = UserSessionRepository.create_session(
            user_id=must_be_int(admin_user.id),
            user_agent="pytest",
            ip_address="127.0.0.1",
            session=session,
        )
        session.commit()

        renewed, new_token = UserSessionRepository.start_or_renew_session(
            user_id=must_be_int(admin_user.id),
            user_agent="pytest",
            ip_address="127.0.0.1",
            session=session,
        )
        session.commit()

        assert renewed.id == original.id
        assert new_token != old_token
        assert (
            UserSessionRepository.get_by_token_opt(token=old_token, session=session)
            is None
        )


class TestSlideOnUse:
    def test_extends_a_session_close_to_expiring(
        self, admin_user: User, session: Session
    ) -> None:
        user_session, _ = UserSessionRepository.create_session(
            user_id=must_be_int(admin_user.id),
            user_agent="pytest",
            ip_address="127.0.0.1",
            session=session,
        )
        user_session.expires_at = BrazilDatetime.now_utc() + timedelta(days=2)

        assert UserSessionRepository.slide_on_use(
            user_session=user_session, session=session
        )
        remaining = user_session.expires_at - BrazilDatetime.now_utc()
        assert remaining > timedelta(days=SESSION_DURATION_DAYS - 1)

    def test_writes_at_most_once_a_day(
        self, admin_user: User, session: Session
    ) -> None:
        user_session, _ = UserSessionRepository.create_session(
            user_id=must_be_int(admin_user.id),
            user_agent="pytest",
            ip_address="127.0.0.1",
            session=session,
        )

        # Just created: already at now + 30 days.
        assert not UserSessionRepository.slide_on_use(
            user_session=user_session, session=session
        )

    def test_never_passes_the_absolute_cap(
        self, admin_user: User, session: Session
    ) -> None:
        user_session, _ = UserSessionRepository.create_session(
            user_id=must_be_int(admin_user.id),
            user_agent="pytest",
            ip_address="127.0.0.1",
            session=session,
        )
        user_session.created_at = BrazilDatetime.now_utc() - timedelta(
            days=SESSION_MAX_AGE_DAYS - 1
        )
        user_session.expires_at = BrazilDatetime.now_utc() + timedelta(hours=1)

        UserSessionRepository.slide_on_use(user_session=user_session, session=session)

        cap = user_session.created_at + timedelta(days=SESSION_MAX_AGE_DAYS)
        assert user_session.expires_at <= cap
