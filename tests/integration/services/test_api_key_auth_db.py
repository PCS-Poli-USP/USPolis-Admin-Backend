"""The DB side of API key authentication, against the test database."""

from sqlmodel import Session

from server.models.database.api_client_db_model import ApiClient
from server.models.database.api_key_db_model import ApiKey
from server.models.database.user_db_model import User
from server.services.security.api_key_auth import (
    db_last_used_writer,
    db_record_loader,
)
from tests.factories.model.api_client_model_factory import ApiClientModelFactory
from tests.factories.model.api_key_model_factory import ApiKeyModelFactory
from tests.factories.model.api_key_rate_limit_model_factory import (
    ApiKeyRateLimitModelFactory,
)


def make_key(admin_user: User, session: Session) -> ApiKey:
    client: ApiClient = ApiClientModelFactory(
        creator=admin_user, session=session
    ).create_and_refresh()
    key = ApiKeyModelFactory(
        client=client, creator=admin_user, session=session
    ).create_and_refresh()
    ApiKeyRateLimitModelFactory(api_key=key, session=session).create_and_refresh(
        max_requests=9, window_seconds=60
    )
    return key


def test_loader_builds_the_record_from_the_database(
    admin_user: User, session: Session
) -> None:
    key = make_key(admin_user, session)

    record = db_record_loader(lambda: session)(key.public_id)

    assert record is not None
    assert (record.id, record.key_hash) == (key.id, key.key_hash)
    assert record.client_active and not record.revoked
    assert [(r.max_requests, r.window_seconds) for r in record.rules] == [(9, 60)]


def test_loader_returns_none_for_an_unknown_key(session: Session) -> None:
    assert db_record_loader(lambda: session)("0123456789abcdef") is None


def test_loader_also_accepts_a_generator_provider(
    admin_user: User, session: Session
) -> None:
    # Production passes get_db, a generator; tests override it with a Session.
    key = make_key(admin_user, session)

    def provider():  # type: ignore[no-untyped-def]
        yield session

    assert db_record_loader(provider)(key.public_id) is not None


def test_last_used_writer_stamps_the_key(admin_user: User, session: Session) -> None:
    key = make_key(admin_user, session)
    assert key.last_used_at is None

    db_last_used_writer(lambda: session)(key.id or 0)
    session.refresh(key)

    assert key.last_used_at is not None
