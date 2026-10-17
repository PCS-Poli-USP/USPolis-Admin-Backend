from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.config import CONFIG
from server.models.database.api_client_db_model import ApiClient
from server.models.database.api_key_db_model import ApiKey
from server.models.database.api_key_delivery_link_db_model import ApiKeyDeliveryLink
from server.models.database.user_db_model import User
from server.models.http.requests.email_request_models import MailSend
from server.repositories.api_key_delivery_link_repository import (
    INVALIDATED_REVOKE_REASON,
)
from server.services.security.api_key_crypto import API_KEY_PATTERN
from server.utils.enums.api_key_link_status_enum import ApiKeyLinkStatus
from tests.factories.model.api_client_model_factory import ApiClientModelFactory
from tests.factories.model.api_key_delivery_link_model_factory import (
    ApiKeyDeliveryLinkModelFactory,
)
from tests.factories.model.api_key_model_factory import ApiKeyModelFactory
from tests.factories.request.api_key_request_factory import ApiKeyRequestFactory

CLIENTS = "/admin/api-clients"
KEYS = "/admin/api-keys"
LINKS = "/admin/api-key-delivery-links"
EMAIL_SERVICE = "server.services.email.email_service"


@pytest.fixture
def api_client(admin_user: User, session: Session) -> ApiClient:
    return ApiClientModelFactory(
        creator=admin_user, session=session
    ).create_and_refresh(contact_email="parceiro@example.com")


@pytest.fixture
def key_factory(
    admin_user: User, session: Session, api_client: ApiClient
) -> ApiKeyModelFactory:
    return ApiKeyModelFactory(client=api_client, creator=admin_user, session=session)


@pytest.fixture
def api_key(key_factory: ApiKeyModelFactory) -> ApiKey:
    return key_factory.create_and_refresh()


@pytest.fixture
def link_factory(
    admin_user: User,
    session: Session,
    key_factory: ApiKeyModelFactory,
    api_key: ApiKey,
) -> ApiKeyDeliveryLinkModelFactory:
    assert key_factory.last_plaintext is not None
    return ApiKeyDeliveryLinkModelFactory(
        api_key=api_key,
        plaintext=key_factory.last_plaintext,
        creator=admin_user,
        session=session,
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


@pytest.fixture
def sent_mail() -> Generator[MagicMock, None, None]:
    """Stub SMTP; outside of production every email goes to SYSTEM_LIST,
    so turn that off to see the real recipient."""
    with (
        patch(f"{EMAIL_SERVICE}.EmailService.send_email_or_raise") as send,
        patch(f"{EMAIL_SERVICE}.SYSTEM_MODE", False),
    ):
        yield send


def via_link_payload(**overrides: Any) -> dict[str, Any]:
    return (
        ApiKeyRequestFactory()
        .create_via_link_input(**overrides)
        .model_dump(mode="json")
    )


class TestAuthorization:
    @pytest.mark.parametrize(
        ("method", "path"),
        [
            ("post", f"{CLIENTS}/1/keys/via-link"),
            ("patch", f"{LINKS}/1/invalidate"),
            ("post", f"{KEYS}/1/share-link/email"),
        ],
    )
    def test_non_admins_are_forbidden(
        self, restricted_client: TestClient, method: str, path: str
    ) -> None:
        response = restricted_client.request(method.upper(), path, json={})

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestCreateViaLink:
    def test_returns_the_link_but_never_the_key(
        self, client: TestClient, api_client: ApiClient
    ) -> None:
        response = client.post(
            f"{CLIENTS}/{api_client.id}/keys/via-link",
            json=via_link_payload(link_ttl_hours=72),
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.headers["cache-control"] == "no-store"
        assert API_KEY_PATTERN.search(response.text) is None
        data = response.json()
        link = data["link"]
        assert link["status"] == ApiKeyLinkStatus.PENDING
        assert data["key"]["delivery_link"]["id"] == link["id"]
        assert data["url"] == (
            f"{CONFIG.frontend_url.rstrip('/')}/api-key/{link['link_id']}#{data['token']}"
        )

    def test_link_lasts_the_chosen_hours(
        self, client: TestClient, api_client: ApiClient, session: Session
    ) -> None:
        response = client.post(
            f"{CLIENTS}/{api_client.id}/keys/via-link",
            json=via_link_payload(link_ttl_hours=1),
        )

        link = session.get(ApiKeyDeliveryLink, response.json()["link"]["id"])
        assert link is not None
        assert (link.expires_at - link.created_at).total_seconds() == 3600

    @pytest.mark.parametrize("hours", [0, 2, 168])
    def test_only_1_24_or_72_hours(
        self, client: TestClient, api_client: ApiClient, hours: int
    ) -> None:
        payload = via_link_payload()
        payload["link_ttl_hours"] = hours

        response = client.post(f"{CLIENTS}/{api_client.id}/keys/via-link", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_unknown_client_is_404(self, client: TestClient) -> None:
        response = client.post(
            f"{CLIENTS}/999999/keys/via-link", json=via_link_payload()
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_key_list_shows_the_link_status(
        self, client: TestClient, api_client: ApiClient
    ) -> None:
        client.post(f"{CLIENTS}/{api_client.id}/keys/via-link", json=via_link_payload())

        keys = client.get(f"{CLIENTS}/{api_client.id}/keys").json()

        assert keys[0]["delivery_link"]["status"] == ApiKeyLinkStatus.PENDING
        assert "token" not in keys[0]["delivery_link"]


class TestInvalidate:
    def test_kills_the_link_and_revokes_the_key(
        self,
        client: TestClient,
        session: Session,
        admin_user: User,
        api_key: ApiKey,
        link: ApiKeyDeliveryLink,
    ) -> None:
        response = client.patch(f"{LINKS}/{link.id}/invalidate")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == ApiKeyLinkStatus.INVALIDATED
        assert response.json()["invalidated_by_id"] == admin_user.id
        session.refresh(api_key)
        assert api_key.revoked_reason == INVALIDATED_REVOKE_REASON

    def test_twice_is_410(self, client: TestClient, link: ApiKeyDeliveryLink) -> None:
        client.patch(f"{LINKS}/{link.id}/invalidate")

        response = client.patch(f"{LINKS}/{link.id}/invalidate")

        assert response.status_code == status.HTTP_410_GONE

    def test_unknown_link_is_404(self, client: TestClient) -> None:
        response = client.patch(f"{LINKS}/999999/invalidate")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestShareLinkByEmail:
    def test_sends_only_the_link_to_the_clients_contact(
        self,
        client: TestClient,
        sent_mail: MagicMock,
        admin_user: User,
        key_factory: ApiKeyModelFactory,
        api_key: ApiKey,
        link: ApiKeyDeliveryLink,
        token: str,
    ) -> None:
        response = client.post(
            f"{KEYS}/{api_key.id}/share-link/email",
            json={"token": token, "message": "Bem-vindos à API!"},
        )

        assert response.status_code == status.HTTP_200_OK
        mail: MailSend = sent_mail.call_args.args[0]
        assert mail.to == ["parceiro@example.com"]
        assert f"/api-key/{link.link_id}#{token}" in mail.body
        assert "Bem-vindos à API!" in mail.body
        assert key_factory.last_plaintext is not None
        assert key_factory.last_plaintext not in mail.body
        assert API_KEY_PATTERN.search(mail.body) is None
        data = response.json()
        assert data["status"] == ApiKeyLinkStatus.PENDING
        assert data["emailed_to"] == "parceiro@example.com"
        assert data["emailed_at"] is not None

    def test_escapes_the_admin_message(
        self,
        client: TestClient,
        sent_mail: MagicMock,
        api_key: ApiKey,
        link: ApiKeyDeliveryLink,
        token: str,
    ) -> None:
        client.post(
            f"{KEYS}/{api_key.id}/share-link/email",
            json={"token": token, "message": '<a href="https://evil.example">x</a>'},
        )

        mail: MailSend = sent_mail.call_args.args[0]
        assert "evil.example" in mail.body
        assert '<a href="https://evil.example">' not in mail.body

    def test_a_wrong_token_is_404_and_sends_nothing(
        self,
        client: TestClient,
        sent_mail: MagicMock,
        api_key: ApiKey,
        link: ApiKeyDeliveryLink,
    ) -> None:
        response = client.post(
            f"{KEYS}/{api_key.id}/share-link/email", json={"token": "wrong"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        sent_mail.assert_not_called()

    def test_an_invalidated_link_is_410(
        self,
        client: TestClient,
        sent_mail: MagicMock,
        api_key: ApiKey,
        link: ApiKeyDeliveryLink,
        token: str,
    ) -> None:
        client.patch(f"{LINKS}/{link.id}/invalidate")

        response = client.post(
            f"{KEYS}/{api_key.id}/share-link/email", json={"token": token}
        )

        assert response.status_code == status.HTTP_410_GONE
        sent_mail.assert_not_called()

    def test_a_key_issued_without_a_link_is_404(
        self, client: TestClient, sent_mail: MagicMock, api_key: ApiKey
    ) -> None:
        response = client.post(
            f"{KEYS}/{api_key.id}/share-link/email", json={"token": "x"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_a_smtp_failure_is_502_and_not_recorded(
        self,
        client: TestClient,
        sent_mail: MagicMock,
        session: Session,
        api_key: ApiKey,
        link: ApiKeyDeliveryLink,
        token: str,
    ) -> None:
        sent_mail.side_effect = OSError("connection refused")

        response = client.post(
            f"{KEYS}/{api_key.id}/share-link/email", json={"token": token}
        )

        assert response.status_code == status.HTTP_502_BAD_GATEWAY
        session.refresh(link)
        assert link.emailed_at is None
        assert link.status() == ApiKeyLinkStatus.PENDING
