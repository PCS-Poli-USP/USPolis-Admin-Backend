from datetime import timedelta
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.api_client_db_model import ApiClient
from server.models.database.api_key_db_model import ApiKey
from server.models.database.user_db_model import User
from server.services.security.api_key_crypto import (
    API_KEY_PATTERN,
    parse_api_key,
    verify_api_key,
)
from server.utils.brazil_datetime import BrazilDatetime
from tests.factories.model.api_client_model_factory import ApiClientModelFactory
from tests.factories.model.api_key_model_factory import ApiKeyModelFactory
from tests.factories.request.api_key_request_factory import (
    ApiClientRequestFactory,
    ApiKeyRequestFactory,
)

CLIENTS = "/admin/api-clients"
KEYS = "/admin/api-keys"


@pytest.fixture
def api_client(admin_user: User, session: Session) -> ApiClient:
    return ApiClientModelFactory(
        creator=admin_user, session=session
    ).create_and_refresh()


@pytest.fixture
def api_key(admin_user: User, session: Session, api_client: ApiClient) -> ApiKey:
    return ApiKeyModelFactory(
        client=api_client, creator=admin_user, session=session
    ).create_and_refresh()


def key_payload(**overrides: Any) -> dict[str, Any]:
    return ApiKeyRequestFactory().create_input(**overrides).model_dump(mode="json")


class TestAuthorization:
    @pytest.mark.parametrize(
        ("method", "path"),
        [
            ("get", CLIENTS),
            ("post", CLIENTS),
            ("get", f"{CLIENTS}/1/keys"),
            ("post", f"{CLIENTS}/1/keys"),
            ("patch", f"{KEYS}/1/revoke"),
        ],
    )
    def test_non_admins_are_forbidden(
        self, restricted_client: TestClient, method: str, path: str
    ) -> None:
        response = restricted_client.request(method.upper(), path, json={})

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestClients:
    def test_create_returns_201_with_the_client(
        self, client: TestClient, admin_user: User
    ) -> None:
        payload = ApiClientRequestFactory().create_input(name="Grêmio Politécnico")

        response = client.post(CLIENTS, json=payload.model_dump())

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Grêmio Politécnico"
        assert data["is_active"] is True
        assert data["created_by_id"] == admin_user.id
        assert (data["active_keys"], data["total_keys"]) == (0, 0)

    def test_create_with_a_taken_name_is_409(
        self, client: TestClient, api_client: ApiClient
    ) -> None:
        payload = ApiClientRequestFactory().create_input(name=api_client.name.upper())

        response = client.post(CLIENTS, json=payload.model_dump())

        assert response.status_code == status.HTTP_409_CONFLICT

    def test_create_with_an_invalid_email_is_422(self, client: TestClient) -> None:
        payload = ApiClientRequestFactory().create_input().model_dump()
        payload["contact_email"] = "not-an-email"

        assert client.post(CLIENTS, json=payload).status_code == 422

    def test_list_and_get(self, client: TestClient, api_client: ApiClient) -> None:
        listed = client.get(CLIENTS).json()
        single = client.get(f"{CLIENTS}/{api_client.id}").json()

        assert [c["id"] for c in listed] == [api_client.id]
        assert single["name"] == api_client.name

    def test_get_unknown_client_is_404(self, client: TestClient) -> None:
        assert client.get(f"{CLIENTS}/999999").status_code == 404

    def test_update(self, client: TestClient, api_client: ApiClient) -> None:
        payload = ApiClientRequestFactory().update_input(contact_name="Nova Diretoria")

        response = client.put(f"{CLIENTS}/{api_client.id}", json=payload.model_dump())

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["contact_name"] == "Nova Diretoria"

    def test_deactivating_disables_its_keys(
        self, client: TestClient, api_client: ApiClient, api_key: ApiKey
    ) -> None:
        response = client.patch(
            f"{CLIENTS}/{api_client.id}/active", json={"is_active": False}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_active"] is False
        assert response.json()["active_keys"] == 0
        key = client.get(f"{KEYS}/{api_key.id}").json()
        assert key["status"] == "client_inactive"

    def test_counts_only_active_keys(
        self,
        client: TestClient,
        admin_user: User,
        session: Session,
        api_client: ApiClient,
        api_key: ApiKey,
    ) -> None:
        ApiKeyModelFactory(
            client=api_client, creator=admin_user, session=session
        ).create_and_refresh(revoked_at=BrazilDatetime.now_utc())

        data = client.get(f"{CLIENTS}/{api_client.id}").json()

        assert (data["active_keys"], data["total_keys"]) == (1, 2)


class TestCreateKey:
    def test_returns_the_key_once_with_no_store(
        self, client: TestClient, session: Session, api_client: ApiClient
    ) -> None:
        response = client.post(f"{CLIENTS}/{api_client.id}/keys", json=key_payload())

        assert response.status_code == status.HTTP_201_CREATED
        assert response.headers["cache-control"] == "no-store"
        data = response.json()
        assert API_KEY_PATTERN.fullmatch(data["key"])
        assert parse_api_key(data["key"]) == data["public_id"]
        stored = session.get(ApiKey, data["id"])
        assert stored is not None
        assert verify_api_key(data["key"], stored.key_hash, stored.hash_version)

    def test_the_key_never_reaches_the_logs(
        self, client: TestClient, api_client: ApiClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        log_calls = MagicMock()
        for level in ("info", "warning", "error"):
            monkeypatch.setattr(
                f"server.middlewares.logger_middleware.logger.{level}", log_calls
            )
        monkeypatch.setattr(
            "server.middlewares.logger_middleware.loki_access_logger.info", log_calls
        )

        data = client.post(f"{CLIENTS}/{api_client.id}/keys", json=key_payload()).json()

        logged = " ".join(str(call) for call in log_calls.call_args_list)
        assert log_calls.called
        assert data["key"] not in logged
        assert data["key"].split("_")[3] not in logged

    def test_later_reads_only_show_the_masked_key(
        self, client: TestClient, api_client: ApiClient
    ) -> None:
        created = client.post(
            f"{CLIENTS}/{api_client.id}/keys", json=key_payload()
        ).json()

        fetched = client.get(f"{KEYS}/{created['id']}").json()
        listed = client.get(f"{CLIENTS}/{api_client.id}/keys").json()

        assert "key" not in fetched and "key_hash" not in fetched
        assert fetched["masked_key"].endswith(f"_{created['public_id']}_****")
        assert created["key"] not in str(listed)

    def test_server_key_without_limits_gets_the_server_defaults(
        self, client: TestClient, api_client: ApiClient
    ) -> None:
        data = client.post(
            f"{CLIENTS}/{api_client.id}/keys", json=key_payload(rate_limits=[])
        ).json()

        assert data["key_type"] == "server"
        assert data["uses_default_limits"] is True
        assert data["rate_limits"] == [
            {"max_requests": 30, "window_seconds": 10},
            {"max_requests": 120, "window_seconds": 60},
            {"max_requests": 10000, "window_seconds": 86400},
        ]

    def test_browser_key_without_limits_gets_the_browser_defaults(
        self, client: TestClient, api_client: ApiClient
    ) -> None:
        data = client.post(
            f"{CLIENTS}/{api_client.id}/keys",
            json=key_payload(
                rate_limits=[], allowed_origins=["https://gremio.poli.usp.br"]
            ),
        ).json()

        assert data["key_type"] == "browser"
        assert data["rate_limits"][0] == {"max_requests": 60, "window_seconds": 10}

    @pytest.mark.parametrize(
        "overrides",
        [
            {"allowed_path_prefixes": []},
            {"allowed_origins": ["https://*.usp.br"]},
            {"expires_at": BrazilDatetime.now_utc() + timedelta(days=400)},
        ],
        ids=["no-prefix", "wildcard-origin", "too-long"],
    )
    def test_invalid_payload_is_422(
        self, client: TestClient, api_client: ApiClient, overrides: dict[str, Any]
    ) -> None:
        payload = key_payload()
        payload.update(
            {
                key: value.isoformat() if hasattr(value, "isoformat") else value
                for key, value in overrides.items()
            }
        )

        response = client.post(f"{CLIENTS}/{api_client.id}/keys", json=payload)

        assert response.status_code == 422

    def test_for_an_unknown_client_is_404(self, client: TestClient) -> None:
        response = client.post(f"{CLIENTS}/999999/keys", json=key_payload())

        assert response.status_code == 404


class TestManageKey:
    def test_update_scope(self, client: TestClient, api_key: ApiKey) -> None:
        payload = (
            ApiKeyRequestFactory()
            .update_input(allowed_path_prefixes=["/allocations", "/buildings"])
            .model_dump(mode="json")
        )

        response = client.put(f"{KEYS}/{api_key.id}", json=payload)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["allowed_path_prefixes"] == [
            "/allocations",
            "/buildings",
        ]

    def test_set_own_rate_limits_then_back_to_defaults(
        self, client: TestClient, api_key: ApiKey
    ) -> None:
        own = client.put(
            f"{KEYS}/{api_key.id}/rate-limits",
            json={"rate_limits": [{"max_requests": 5, "window_seconds": 1}]},
        ).json()
        defaults = client.put(
            f"{KEYS}/{api_key.id}/rate-limits", json={"rate_limits": []}
        ).json()

        assert own["uses_default_limits"] is False
        assert own["rate_limits"] == [{"max_requests": 5, "window_seconds": 1}]
        assert defaults["uses_default_limits"] is True

    def test_duplicate_windows_are_422(
        self, client: TestClient, api_key: ApiKey
    ) -> None:
        response = client.put(
            f"{KEYS}/{api_key.id}/rate-limits",
            json={
                "rate_limits": [
                    {"max_requests": 5, "window_seconds": 60},
                    {"max_requests": 9, "window_seconds": 60},
                ]
            },
        )

        assert response.status_code == 422

    def test_revoke_records_the_audit_trail(
        self, client: TestClient, admin_user: User, api_key: ApiKey
    ) -> None:
        response = client.patch(
            f"{KEYS}/{api_key.id}/revoke", json={"reason": "Vazou no GitHub"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "revoked"
        assert data["revoked_by_id"] == admin_user.id
        assert data["revoked_reason"] == "Vazou no GitHub"

    def test_revoke_requires_a_reason(
        self, client: TestClient, api_key: ApiKey
    ) -> None:
        response = client.patch(f"{KEYS}/{api_key.id}/revoke", json={"reason": ""})

        assert response.status_code == 422

    def test_revoked_key_is_final(self, client: TestClient, api_key: ApiKey) -> None:
        client.patch(f"{KEYS}/{api_key.id}/revoke", json={"reason": "motivo"})

        again = client.patch(f"{KEYS}/{api_key.id}/revoke", json={"reason": "outro"})
        edit = client.put(
            f"{KEYS}/{api_key.id}",
            json=ApiKeyRequestFactory().update_input().model_dump(mode="json"),
        )

        assert again.status_code == status.HTTP_409_CONFLICT
        assert edit.status_code == status.HTTP_409_CONFLICT

    def test_expired_key_is_reported_as_expired(
        self,
        client: TestClient,
        admin_user: User,
        session: Session,
        api_client: ApiClient,
    ) -> None:
        now = BrazilDatetime.now_utc()
        key = ApiKeyModelFactory(
            client=api_client, creator=admin_user, session=session
        ).create_and_refresh(
            created_at=now - timedelta(days=10), expires_at=now - timedelta(days=1)
        )

        assert client.get(f"{KEYS}/{key.id}").json()["status"] == "expired"

    def test_unknown_key_is_404(self, client: TestClient) -> None:
        assert client.get(f"{KEYS}/999999").status_code == 404
