from collections.abc import Generator
from datetime import timedelta
from typing import Any

import pytest
from sqlalchemy import event, text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from server.models.database.api_client_db_model import ApiClient
from server.models.database.api_key_db_model import ApiKey
from server.models.database.api_key_delivery_link_db_model import ApiKeyDeliveryLink
from server.models.database.user_db_model import User
from server.repositories.api_key_repository import ApiKeyRepository
from server.repositories.api_key_delivery_link_repository import (
    EXPIRED_REVOKE_REASON,
    INVALIDATED_REVOKE_REASON,
    ApiKeyDeliveryLinkRepository,
    ApiKeyLinkGone,
    ApiKeyLinkNotFound,
)
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.api_key_link_status_enum import ApiKeyLinkStatus
from tests.factories.model.api_client_model_factory import ApiClientModelFactory
from tests.factories.model.api_key_delivery_link_model_factory import (
    ApiKeyDeliveryLinkModelFactory,
)
from tests.factories.model.api_key_model_factory import ApiKeyModelFactory

IP = "203.0.113.7"
USER_AGENT = "Mozilla/5.0 (test)"


@pytest.fixture
def api_client(admin_user: User, session: Session) -> ApiClient:
    return ApiClientModelFactory(
        creator=admin_user, session=session
    ).create_and_refresh()


@pytest.fixture
def key_factory(
    admin_user: User, session: Session, api_client: ApiClient
) -> ApiKeyModelFactory:
    return ApiKeyModelFactory(client=api_client, creator=admin_user, session=session)


@pytest.fixture
def api_key(key_factory: ApiKeyModelFactory) -> ApiKey:
    return key_factory.create_and_refresh()


@pytest.fixture
def plaintext(key_factory: ApiKeyModelFactory, api_key: ApiKey) -> str:
    assert key_factory.last_plaintext is not None
    return key_factory.last_plaintext


@pytest.fixture
def link_factory(
    admin_user: User, session: Session, api_key: ApiKey, plaintext: str
) -> ApiKeyDeliveryLinkModelFactory:
    return ApiKeyDeliveryLinkModelFactory(
        api_key=api_key, plaintext=plaintext, creator=admin_user, session=session
    )


@pytest.fixture
def link(link_factory: ApiKeyDeliveryLinkModelFactory) -> ApiKeyDeliveryLink:
    return link_factory.create_and_refresh()


@pytest.fixture
def token(
    link_factory: ApiKeyDeliveryLinkModelFactory, link: ApiKeyDeliveryLink
) -> str:
    assert link_factory.last_token is not None
    return link_factory.last_token


def reveal(session: Session, link: ApiKeyDeliveryLink, token: str) -> str:
    revealed, plaintext = ApiKeyDeliveryLinkRepository.reveal(
        link_id=link.link_id, token=token, ip=IP, user_agent=USER_AGENT, session=session
    )
    assert revealed == link
    return plaintext


def expired_overrides() -> dict[str, Any]:
    now = BrazilDatetime.now_utc()
    return {
        "created_at": now - timedelta(hours=2),
        "expires_at": now - timedelta(hours=1),
    }


@pytest.fixture
def captured_sql(session: Session) -> Generator[list[str], None, None]:
    statements: list[str] = []

    def capture(*args: Any) -> None:
        statements.append(args[2])

    connection = session.connection()
    event.listen(connection, "before_cursor_execute", capture)
    yield statements
    event.remove(connection, "before_cursor_execute", capture)


class TestCreateForKey:
    def test_returns_a_token_that_opens_the_key(
        self, admin_user: User, session: Session, api_key: ApiKey, plaintext: str
    ) -> None:
        link, token = ApiKeyDeliveryLinkRepository.create_for_key(
            key=api_key,
            plaintext=plaintext,
            ttl=timedelta(hours=24),
            user=admin_user,
            session=session,
        )
        session.commit()
        session.refresh(link)

        assert ApiKeyDeliveryLinkRepository.open(link=link, token=token) == plaintext
        assert link.status() == ApiKeyLinkStatus.PENDING
        assert link.created_by_id == admin_user.id
        assert link.expires_at - link.created_at == timedelta(hours=24)
        assert api_key.delivery_link == link

    def test_neither_the_key_nor_the_token_is_persisted(
        self, admin_user: User, session: Session, api_key: ApiKey, plaintext: str
    ) -> None:
        link, token = ApiKeyDeliveryLinkRepository.create_for_key(
            key=api_key,
            plaintext=plaintext,
            ttl=timedelta(hours=1),
            user=admin_user,
            session=session,
        )
        session.commit()

        row = session.exec(  # type: ignore[call-overload]
            text("SELECT * FROM apikeydeliverylink WHERE id = :id"),
            params={"id": link.id},
        ).one()
        stored = " ".join(
            value.hex() if isinstance(value, bytes) else str(value) for value in row
        )
        raw = b"".join(value for value in row if isinstance(value, bytes))
        assert plaintext not in stored
        assert plaintext.encode() not in raw
        assert token not in stored
        assert token.encode() not in raw

    def test_a_key_has_at_most_one_link(
        self, admin_user: User, session: Session, api_key: ApiKey, plaintext: str
    ) -> None:
        def create() -> None:
            ApiKeyDeliveryLinkRepository.create_for_key(
                key=api_key,
                plaintext=plaintext,
                ttl=timedelta(hours=1),
                user=admin_user,
                session=session,
            )

        create()
        with pytest.raises(IntegrityError):
            create()


class TestReveal:
    def test_returns_the_key_once_and_records_who_opened_it(
        self, session: Session, link: ApiKeyDeliveryLink, token: str, plaintext: str
    ) -> None:
        assert reveal(session, link, token) == plaintext
        session.commit()
        session.refresh(link)

        assert link.status() == ApiKeyLinkStatus.CONSUMED
        assert link.consumed_ip == IP
        assert link.consumed_user_agent == USER_AGENT
        assert link.ciphertext is None
        assert link.nonce is None
        assert link.salt is None

    def test_a_second_reveal_is_gone(
        self, session: Session, link: ApiKeyDeliveryLink, token: str
    ) -> None:
        reveal(session, link, token)
        session.commit()

        with pytest.raises(ApiKeyLinkGone):
            reveal(session, link, token)

    def test_a_wrong_token_does_not_burn_the_link(
        self,
        session: Session,
        link: ApiKeyDeliveryLink,
        token: str,
        plaintext: str,
    ) -> None:
        wrong = token[:-1] + ("A" if token[-1] != "A" else "B")

        with pytest.raises(ApiKeyLinkNotFound):
            reveal(session, link, wrong)
        session.refresh(link)

        assert link.status() == ApiKeyLinkStatus.PENDING
        assert link.ciphertext is not None
        assert reveal(session, link, token) == plaintext

    def test_an_unknown_link_is_not_found(self, session: Session) -> None:
        with pytest.raises(ApiKeyLinkNotFound):
            ApiKeyDeliveryLinkRepository.reveal(
                link_id="0" * 16, token="x", ip=None, user_agent=None, session=session
            )

    def test_locks_the_row(
        self,
        session: Session,
        link: ApiKeyDeliveryLink,
        token: str,
        captured_sql: list[str],
    ) -> None:
        """Two concurrent reveals must not both see the link pending."""
        reveal(session, link, token)

        lookups = [sql for sql in captured_sql if "FROM apikeydeliverylink" in sql]
        assert lookups
        assert "FOR UPDATE" in lookups[0]

    def test_an_expired_link_is_gone(
        self,
        session: Session,
        link_factory: ApiKeyDeliveryLinkModelFactory,
    ) -> None:
        link = link_factory.create_and_refresh(**expired_overrides())
        assert link_factory.last_token is not None

        with pytest.raises(ApiKeyLinkGone):
            reveal(session, link, link_factory.last_token)

    def test_a_revoked_key_is_gone(
        self,
        admin_user: User,
        session: Session,
        api_key: ApiKey,
        link: ApiKeyDeliveryLink,
        token: str,
    ) -> None:
        api_key.revoked_at = BrazilDatetime.now_utc()
        api_key.revoked_by_id = admin_user.id
        session.add(api_key)
        session.commit()

        with pytest.raises(ApiKeyLinkGone):
            reveal(session, link, token)

    def test_an_inactive_client_is_gone(
        self,
        session: Session,
        api_client: ApiClient,
        link: ApiKeyDeliveryLink,
        token: str,
    ) -> None:
        api_client.is_active = False
        session.add(api_client)
        session.commit()

        with pytest.raises(ApiKeyLinkGone):
            reveal(session, link, token)


class TestInvalidate:
    def test_wipes_the_link_and_revokes_its_key(
        self,
        admin_user: User,
        session: Session,
        api_key: ApiKey,
        link: ApiKeyDeliveryLink,
    ) -> None:
        ApiKeyDeliveryLinkRepository.invalidate(
            id=link.id or 0, user=admin_user, session=session
        )
        session.commit()
        session.refresh(link)
        session.refresh(api_key)

        assert link.status() == ApiKeyLinkStatus.INVALIDATED
        assert link.invalidated_by_id == admin_user.id
        assert link.ciphertext is None
        assert api_key.revoked_at is not None
        assert api_key.revoked_by_id == admin_user.id
        assert api_key.revoked_reason == INVALIDATED_REVOKE_REASON

    def test_a_consumed_link_cannot_be_invalidated(
        self,
        admin_user: User,
        session: Session,
        api_key: ApiKey,
        link: ApiKeyDeliveryLink,
        token: str,
    ) -> None:
        reveal(session, link, token)
        session.commit()

        with pytest.raises(ApiKeyLinkGone):
            ApiKeyDeliveryLinkRepository.invalidate(
                id=link.id or 0, user=admin_user, session=session
            )
        session.refresh(api_key)
        assert api_key.revoked_at is None

    def test_keeps_an_earlier_revocation(
        self,
        admin_user: User,
        session: Session,
        api_key: ApiKey,
        link: ApiKeyDeliveryLink,
    ) -> None:
        revoked_at = BrazilDatetime.now_utc() - timedelta(minutes=5)
        api_key.revoked_at = revoked_at
        api_key.revoked_reason = "vazou"
        session.add(api_key)
        session.commit()

        ApiKeyDeliveryLinkRepository.invalidate(
            id=link.id or 0, user=admin_user, session=session
        )
        session.commit()
        session.refresh(api_key)

        assert api_key.revoked_at == revoked_at
        assert api_key.revoked_reason == "vazou"

    def test_an_unknown_link_is_not_found(
        self, admin_user: User, session: Session
    ) -> None:
        with pytest.raises(ApiKeyLinkNotFound):
            ApiKeyDeliveryLinkRepository.invalidate(
                id=999999, user=admin_user, session=session
            )


class TestExpirePending:
    def test_wipes_and_revokes_only_links_that_expired_unopened(
        self,
        admin_user: User,
        session: Session,
        api_client: ApiClient,
        key_factory: ApiKeyModelFactory,
    ) -> None:
        def new_link(**overrides: Any) -> ApiKeyDeliveryLink:
            key = key_factory.create_and_refresh()
            assert key_factory.last_plaintext is not None
            factory = ApiKeyDeliveryLinkModelFactory(
                api_key=key,
                plaintext=key_factory.last_plaintext,
                creator=admin_user,
                session=session,
            )
            return factory.create_and_refresh(**overrides)

        expired = new_link(**expired_overrides())
        pending = new_link()
        consumed = new_link(
            **expired_overrides(),
            consumed_at=BrazilDatetime.now_utc() - timedelta(minutes=90),
            ciphertext=None,
            nonce=None,
            salt=None,
        )

        expired_links = ApiKeyDeliveryLinkRepository.expire_pending(
            now=BrazilDatetime.now_utc(), session=session
        )
        session.commit()
        for row in (expired, pending, consumed):
            session.refresh(row)
            session.refresh(row.api_key)

        assert expired_links == [expired]
        assert expired.status() == ApiKeyLinkStatus.INVALIDATED
        assert expired.invalidated_by_id is None
        assert expired.ciphertext is None
        assert expired.api_key.revoked_reason == EXPIRED_REVOKE_REASON
        assert expired.api_key.revoked_by_id is None
        assert pending.status() == ApiKeyLinkStatus.PENDING
        assert pending.ciphertext is not None
        assert pending.api_key.revoked_at is None
        assert consumed.status() == ApiKeyLinkStatus.CONSUMED
        assert consumed.api_key.revoked_at is None


class TestGetPendingForKey:
    def test_checks_the_token_without_consuming_the_link(
        self, session: Session, api_key: ApiKey, link: ApiKeyDeliveryLink, token: str
    ) -> None:
        found = ApiKeyDeliveryLinkRepository.get_pending_for_key(
            key=api_key, token=token
        )

        assert found == link
        assert link.status() == ApiKeyLinkStatus.PENDING
        assert link.ciphertext is not None

    def test_a_wrong_token_is_not_found(
        self, api_key: ApiKey, link: ApiKeyDeliveryLink
    ) -> None:
        with pytest.raises(ApiKeyLinkNotFound):
            ApiKeyDeliveryLinkRepository.get_pending_for_key(key=api_key, token="x")

    def test_a_key_without_a_link_is_not_found(self, api_key: ApiKey) -> None:
        with pytest.raises(ApiKeyLinkNotFound):
            ApiKeyDeliveryLinkRepository.get_pending_for_key(key=api_key, token="x")

    def test_a_consumed_link_is_gone(
        self, session: Session, api_key: ApiKey, link: ApiKeyDeliveryLink, token: str
    ) -> None:
        reveal(session, link, token)
        session.commit()

        with pytest.raises(ApiKeyLinkGone):
            ApiKeyDeliveryLinkRepository.get_pending_for_key(key=api_key, token=token)


class TestMarkEmailed:
    def test_records_who_sent_it_and_to_whom(
        self, admin_user: User, session: Session, link: ApiKeyDeliveryLink
    ) -> None:
        ApiKeyDeliveryLinkRepository.mark_emailed(
            link=link, to=["a@usp.br", "b@usp.br"], user=admin_user, session=session
        )
        session.commit()
        session.refresh(link)

        assert link.emailed_at is not None
        assert link.emailed_to == "a@usp.br, b@usp.br"
        assert link.emailed_by_id == admin_user.id
        assert link.status() == ApiKeyLinkStatus.PENDING


class TestRevokingTheKey:
    def test_kills_its_pending_link(
        self,
        admin_user: User,
        session: Session,
        api_key: ApiKey,
        link: ApiKeyDeliveryLink,
    ) -> None:
        ApiKeyRepository.revoke(
            id=api_key.id or 0, reason="vazou", user=admin_user, session=session
        )
        session.commit()
        session.refresh(link)

        assert link.status() == ApiKeyLinkStatus.INVALIDATED
        assert link.invalidated_by_id == admin_user.id
        assert link.ciphertext is None

    def test_leaves_a_consumed_link_as_it_was(
        self,
        admin_user: User,
        session: Session,
        api_key: ApiKey,
        link: ApiKeyDeliveryLink,
        token: str,
    ) -> None:
        reveal(session, link, token)
        session.commit()

        ApiKeyRepository.revoke(
            id=api_key.id or 0, reason="vazou", user=admin_user, session=session
        )
        session.commit()
        session.refresh(link)

        assert link.status() == ApiKeyLinkStatus.CONSUMED
        assert link.invalidated_at is None


class TestConstraints:
    def test_a_dead_link_cannot_hold_the_sealed_key(
        self, session: Session, link: ApiKeyDeliveryLink
    ) -> None:
        link.consumed_at = BrazilDatetime.now_utc()
        session.add(link)

        with pytest.raises(IntegrityError):
            session.flush()
