"""End to end through the real app: ApiKeyMiddleware loading keys from the
test database (via the get_db override), with the real route table."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.config import CONFIG
from server.models.database.api_client_db_model import ApiClient
from server.models.database.user_db_model import User
from server.repositories.api_client_repository import ApiClientRepository
from server.repositories.api_key_repository import ApiKeyRepository
from tests.factories.model.api_client_model_factory import ApiClientModelFactory
from tests.factories.model.api_key_model_factory import ApiKeyModelFactory

# Whatever the running .env allows; CORS for it must stay as before.
FIRST_PARTY = CONFIG.allowed_origins[0]


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


def issue(factory: ApiKeyModelFactory, **overrides: object) -> tuple[int, str]:
    key = factory.create_and_refresh(**overrides)  # type: ignore[arg-type]
    assert factory.last_plaintext is not None
    return key.id or 0, factory.last_plaintext


def test_valid_key_reaches_a_public_route(
    public_client: TestClient, key_factory: ApiKeyModelFactory
) -> None:
    _, plaintext = issue(key_factory, allowed_path_prefixes=["/buildings"])

    response = public_client.get("/buildings", headers={"X-API-Key": plaintext})

    assert response.status_code == status.HTTP_200_OK


def test_requests_without_a_key_still_work_anonymously(
    public_client: TestClient,
) -> None:
    assert public_client.get("/buildings").status_code == status.HTTP_200_OK


def test_public_route_outside_the_keys_scope_is_403(
    public_client: TestClient, key_factory: ApiKeyModelFactory
) -> None:
    _, plaintext = issue(key_factory, allowed_path_prefixes=["/allocations"])

    response = public_client.get("/buildings", headers={"X-API-Key": plaintext})

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_key_never_opens_a_non_public_route(
    public_client: TestClient, key_factory: ApiKeyModelFactory
) -> None:
    # Even with "/" (every public route), an authenticated route stays shut.
    _, plaintext = issue(key_factory, allowed_path_prefixes=["/"])

    response = public_client.get("/users/my-classes", headers={"X-API-Key": plaintext})

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_revocation_takes_effect_on_the_next_request(
    public_client: TestClient,
    key_factory: ApiKeyModelFactory,
    admin_user: User,
    session: Session,
) -> None:
    key_id, plaintext = issue(key_factory, allowed_path_prefixes=["/buildings"])
    headers = {"X-API-Key": plaintext}
    assert public_client.get("/buildings", headers=headers).status_code == 200

    ApiKeyRepository.revoke(id=key_id, reason="vazou", user=admin_user, session=session)
    session.commit()

    assert public_client.get("/buildings", headers=headers).status_code == 401


def test_deactivating_the_client_blocks_its_keys(
    public_client: TestClient,
    key_factory: ApiKeyModelFactory,
    api_client: ApiClient,
    session: Session,
) -> None:
    _, plaintext = issue(key_factory, allowed_path_prefixes=["/buildings"])

    ApiClientRepository.set_active(
        id=api_client.id or 0, is_active=False, session=session
    )
    session.commit()

    response = public_client.get("/buildings", headers={"X-API-Key": plaintext})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_key_in_the_url_is_refused(public_client: TestClient) -> None:
    response = public_client.get("/buildings", params={"api_key": "anything"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_rejection_keeps_cors_headers_for_allowed_origins(
    public_client: TestClient,
) -> None:
    # ApiKeyMiddleware runs inside CORS, so the browser can read the 401.
    response = public_client.get(
        "/buildings",
        headers={"X-API-Key": "garbage", "Origin": FIRST_PARTY},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["access-control-allow-origin"] == FIRST_PARTY
