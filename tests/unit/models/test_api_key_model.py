from datetime import timedelta

from sqlmodel import Session

from server.models.database.api_client_db_model import ApiClient
from server.models.database.user_db_model import User
from server.utils.brazil_datetime import BrazilDatetime
from tests.factories.model.api_client_model_factory import ApiClientModelFactory
from tests.factories.model.api_key_model_factory import ApiKeyModelFactory

NOW = BrazilDatetime.now_utc()


def build_client(is_active: bool = True) -> ApiClient:
    creator = User(id=1, name="admin", email="admin@usp.br")
    client = ApiClientModelFactory(creator=creator, session=Session()).build(
        is_active=is_active
    )
    client.id = 1
    return client


def build_key_factory(client: ApiClient) -> ApiKeyModelFactory:
    creator = User(id=1, name="admin", email="admin@usp.br")
    return ApiKeyModelFactory(client=client, creator=creator, session=Session())


class TestIsUsable:
    def test_active_unexpired_unrevoked_key_is_usable(self) -> None:
        client = build_client()
        key = build_key_factory(client).build(expires_at=NOW + timedelta(days=1))
        key.client = client

        assert key.is_usable(NOW)

    def test_expired_key_is_not_usable(self) -> None:
        client = build_client()
        key = build_key_factory(client).build(expires_at=NOW - timedelta(seconds=1))
        key.client = client

        assert not key.is_usable(NOW)

    def test_revoked_key_is_not_usable(self) -> None:
        client = build_client()
        key = build_key_factory(client).build(revoked_at=NOW - timedelta(hours=1))
        key.client = client

        assert not key.is_usable(NOW)

    def test_key_of_an_inactive_client_is_not_usable(self) -> None:
        client = build_client(is_active=False)
        key = build_key_factory(client).build()
        key.client = client

        assert not key.is_usable(NOW)


def test_browser_key_is_one_with_allowed_origins() -> None:
    factory = build_key_factory(build_client())

    assert not factory.build(allowed_origins=[]).is_browser_key
    assert factory.build(allowed_origins=["https://site.com"]).is_browser_key
