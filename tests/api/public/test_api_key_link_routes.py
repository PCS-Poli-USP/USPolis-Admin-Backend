"""The partner's side of one-time delivery links, through the real app."""

from datetime import timedelta

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.api_client_db_model import ApiClient
from server.models.database.api_key_db_model import ApiKey
from server.models.database.api_key_delivery_link_db_model import ApiKeyDeliveryLink
from server.models.database.user_db_model import User
from server.repositories.api_key_delivery_link_repository import (
    ApiKeyDeliveryLinkRepository,
)
from server.repositories.api_key_repository import ApiKeyRepository
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.api_key_link_status_enum import ApiKeyLinkStatus
from tests.factories.model.api_client_model_factory import ApiClientModelFactory
from tests.factories.model.api_key_delivery_link_model_factory import (
    ApiKeyDeliveryLinkModelFactory,
)
from tests.factories.model.api_key_model_factory import ApiKeyModelFactory
from tests.factories.request.api_key_request_factory import ApiKeyRequestFactory

LINKS = "/api-key-links"
PRIVATE_HEADERS = {
    "cache-control": "no-store",
    "referrer-policy": "no-referrer",
    "x-robots-tag": "noindex",
}


@pytest.fixture
def api_client(admin_user: User, session: Session) -> ApiClient:
    return ApiClientModelFactory(
        creator=admin_user, session=session
    ).create_and_refresh(name="Grêmio Politécnico")


@pytest.fixture
def key_factory(
    admin_user: User, session: Session, api_client: ApiClient
) -> ApiKeyModelFactory:
    return ApiKeyModelFactory(client=api_client, creator=admin_user, session=session)


@pytest.fixture
def api_key(key_factory: ApiKeyModelFactory) -> ApiKey:
    return key_factory.create_and_refresh(name="Site do grêmio")


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


def assert_private(headers: dict[str, str] | object) -> None:
    for name, value in PRIVATE_HEADERS.items():
        assert headers[name] == value  # type: ignore[index]


class TestStatus:
    def test_shows_the_link_without_any_secret(
        self, public_client: TestClient, link: ApiKeyDeliveryLink, plaintext: str
    ) -> None:
        response = public_client.get(f"{LINKS}/{link.link_id}")

        assert response.status_code == status.HTTP_200_OK
        assert_private(response.headers)
        assert response.json() == {
            "status": ApiKeyLinkStatus.PENDING,
            "available": True,
            "expires_at": link.expires_at.isoformat(),
            "client_name": "Grêmio Politécnico",
            "key_name": "Site do grêmio",
        }
        assert plaintext not in response.text

    def test_does_not_consume_the_link(
        self,
        public_client: TestClient,
        session: Session,
        link: ApiKeyDeliveryLink,
    ) -> None:
        for _ in range(3):
            public_client.get(f"{LINKS}/{link.link_id}")

        session.refresh(link)
        assert link.status() == ApiKeyLinkStatus.PENDING
        assert link.ciphertext is not None

    def test_a_link_of_an_inactive_client_is_not_available(
        self,
        public_client: TestClient,
        session: Session,
        api_client: ApiClient,
        link: ApiKeyDeliveryLink,
    ) -> None:
        api_client.is_active = False
        session.add(api_client)
        session.commit()

        data = public_client.get(f"{LINKS}/{link.link_id}").json()

        assert data["status"] == ApiKeyLinkStatus.PENDING
        assert data["available"] is False

    def test_unknown_link_is_404(self, public_client: TestClient) -> None:
        response = public_client.get(f"{LINKS}/{'0' * 16}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_malformed_link_id_is_422(self, public_client: TestClient) -> None:
        response = public_client.get(f"{LINKS}/not-a-link")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestReveal:
    def test_returns_the_key_once(
        self,
        public_client: TestClient,
        link: ApiKeyDeliveryLink,
        token: str,
        plaintext: str,
        api_key: ApiKey,
    ) -> None:
        response = public_client.post(
            f"{LINKS}/{link.link_id}/reveal",
            json={"token": token},
            headers={"User-Agent": "parceiro-test"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert_private(response.headers)
        data = response.json()
        assert data["key"] == plaintext
        assert data["client_name"] == "Grêmio Politécnico"
        assert data["allowed_path_prefixes"] == api_key.allowed_path_prefixes

        again = public_client.post(
            f"{LINKS}/{link.link_id}/reveal", json={"token": token}
        )
        assert again.status_code == status.HTTP_410_GONE
        assert plaintext not in again.text

    def test_records_who_opened_it(
        self,
        public_client: TestClient,
        session: Session,
        link: ApiKeyDeliveryLink,
        token: str,
    ) -> None:
        public_client.post(
            f"{LINKS}/{link.link_id}/reveal",
            json={"token": token},
            headers={"User-Agent": "parceiro-test"},
        )

        session.refresh(link)
        assert link.status() == ApiKeyLinkStatus.CONSUMED
        assert link.consumed_user_agent == "parceiro-test"
        assert link.consumed_ip is not None
        assert link.ciphertext is None

    def test_a_wrong_token_is_404_and_keeps_the_link(
        self,
        public_client: TestClient,
        link: ApiKeyDeliveryLink,
        token: str,
        plaintext: str,
    ) -> None:
        wrong = public_client.post(
            f"{LINKS}/{link.link_id}/reveal", json={"token": "wrong"}
        )
        right = public_client.post(
            f"{LINKS}/{link.link_id}/reveal", json={"token": token}
        )

        assert wrong.status_code == status.HTTP_404_NOT_FOUND
        assert right.status_code == status.HTTP_200_OK
        assert right.json()["key"] == plaintext

    def test_an_expired_link_is_410(
        self, public_client: TestClient, link_factory: ApiKeyDeliveryLinkModelFactory
    ) -> None:
        now = BrazilDatetime.now_utc()
        link = link_factory.create_and_refresh(
            created_at=now - timedelta(hours=2), expires_at=now - timedelta(hours=1)
        )

        response = public_client.post(
            f"{LINKS}/{link.link_id}/reveal", json={"token": link_factory.last_token}
        )

        assert response.status_code == status.HTTP_410_GONE

    def test_a_missing_token_is_422(
        self, public_client: TestClient, link: ApiKeyDeliveryLink
    ) -> None:
        response = public_client.post(f"{LINKS}/{link.link_id}/reveal", json={})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_full_flow_issue_reveal_and_use_the_key(
    public_client: TestClient,
    session: Session,
    admin_user: User,
    api_client: ApiClient,
) -> None:
    """What a partner lives through: an admin issues a key by link, the
    partner reveals it and calls a public route with it."""
    input = ApiKeyRequestFactory().create_via_link_input(
        allowed_path_prefixes=["/buildings"]
    )
    key, plaintext = ApiKeyRepository.create(
        client_id=api_client.id or 0, input=input, user=admin_user, session=session
    )
    link, token = ApiKeyDeliveryLinkRepository.create_for_key(
        key=key,
        plaintext=plaintext,
        ttl=timedelta(hours=input.link_ttl_hours),
        user=admin_user,
        session=session,
    )
    session.commit()

    revealed = public_client.post(
        f"{LINKS}/{link.link_id}/reveal", json={"token": token}
    ).json()["key"]
    response = public_client.get("/buildings", headers={"X-API-Key": revealed})

    assert revealed == plaintext
    assert response.status_code == status.HTTP_200_OK
