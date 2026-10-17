"""Partner CORS through the real app: origins come from browser keys in the
test database (PartnerCorsMiddleware's cache is off in tests)."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.config import CONFIG
from server.models.database.api_client_db_model import ApiClient
from server.models.database.user_db_model import User
from server.repositories.api_key_repository import ApiKeyRepository
from tests.factories.model.api_client_model_factory import ApiClientModelFactory
from tests.factories.model.api_key_model_factory import ApiKeyModelFactory

PARTNER = "https://gremio.poli.usp.br"

# Whatever the running .env allows; CORS for it must stay as before.
FIRST_PARTY = CONFIG.allowed_origins[0]


@pytest.fixture
def browser_key(admin_user: User, session: Session) -> tuple[int, str]:
    client: ApiClient = ApiClientModelFactory(
        creator=admin_user, session=session
    ).create_and_refresh()
    factory = ApiKeyModelFactory(client=client, creator=admin_user, session=session)
    key = factory.create_and_refresh(
        allowed_path_prefixes=["/buildings"], allowed_origins=[PARTNER]
    )
    assert factory.last_plaintext is not None
    return key.id or 0, factory.last_plaintext


def preflight(client: TestClient, origin: str) -> object:
    return client.options(
        "/buildings",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "x-api-key",
        },
    )


def test_partner_site_can_call_with_its_browser_key(
    public_client: TestClient, browser_key: tuple[int, str]
) -> None:
    _, plaintext = browser_key

    pre = preflight(public_client, PARTNER)
    response = public_client.get(
        "/buildings", headers={"Origin": PARTNER, "X-API-Key": plaintext}
    )

    assert pre.status_code == 200  # type: ignore[attr-defined]
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == PARTNER
    assert "access-control-allow-credentials" not in response.headers


def test_an_unregistered_site_is_refused(
    public_client: TestClient, browser_key: tuple[int, str]
) -> None:
    assert preflight(public_client, "https://evil.com").status_code == 400  # type: ignore[attr-defined]


def test_revoking_the_key_closes_cors_for_its_site(
    public_client: TestClient,
    browser_key: tuple[int, str],
    admin_user: User,
    session: Session,
) -> None:
    key_id, _ = browser_key
    ApiKeyRepository.revoke(
        id=key_id, reason="fim da parceria", user=admin_user, session=session
    )
    session.commit()

    assert preflight(public_client, PARTNER).status_code == 400  # type: ignore[attr-defined]


def test_first_party_frontend_is_unchanged(public_client: TestClient) -> None:
    response = public_client.get("/buildings", headers={"Origin": FIRST_PARTY})

    assert response.headers["access-control-allow-origin"] == FIRST_PARTY
    assert response.headers["access-control-allow-credentials"] == "true"
