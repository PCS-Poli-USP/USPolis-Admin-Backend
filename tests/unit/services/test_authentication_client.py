from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import requests
from fastapi import HTTPException

from server.config import CONFIG
from server.services.auth.authentication_client import (
    GOOGLE_REQUEST_TIMEOUT_SECONDS,
    INVALID_TOKEN_CACHE_SECONDS,
    USER_INFO_CACHE_SECONDS,
    AuthenticationClient,
    AuthProviderUnavailable,
)


def make_response(*, status_code: int, json_data: Any) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data
    return response


class TestVerifyAccessToken:
    def test_returns_token_info_on_success(self) -> None:
        token_info = {"scope": "email profile", "expires_in": 3600}
        with patch(
            "server.services.auth.authentication_client.requests.get",
            return_value=make_response(status_code=200, json_data=token_info),
        ):
            assert AuthenticationClient.verify_access_token("a-token") == token_info

    def test_raises_401_when_token_is_invalid(self) -> None:
        with patch(
            "server.services.auth.authentication_client.requests.get",
            return_value=make_response(status_code=400, json_data={"error": "invalid"}),
        ):
            with pytest.raises(HTTPException) as exc_info:
                AuthenticationClient.verify_access_token("bad-token")

        assert exc_info.value.status_code == 401


class TestGetUserInfo:
    _valid_payload = {
        "email": "user@usp.br",
        "email_verified": True,
        "name": "User Name",
        "picture": "https://example.com/pic.png",
        "given_name": "User",
        "family_name": "Name",
    }

    def test_returns_auth_user_info_when_domain_is_allowed(self) -> None:
        with (
            patch.object(CONFIG, "allowed_gmails_domains", ["usp.br"]),
            patch.object(CONFIG, "allowed_gmails", []),
            patch(
                "server.services.auth.authentication_client.requests.get",
                return_value=make_response(
                    status_code=200, json_data=self._valid_payload
                ),
            ),
        ):
            info = AuthenticationClient.get_user_info("a-token")

        assert info.email == "user@usp.br"
        assert info.domain == "usp.br"

    def test_returns_auth_user_info_when_email_is_individually_allowlisted(
        self,
    ) -> None:
        # Domain not allowed, but the exact email is in the allowlist.
        with (
            patch.object(CONFIG, "allowed_gmails_domains", ["other.br"]),
            patch.object(CONFIG, "allowed_gmails", ["user@usp.br"]),
            patch(
                "server.services.auth.authentication_client.requests.get",
                return_value=make_response(
                    status_code=200, json_data=self._valid_payload
                ),
            ),
        ):
            info = AuthenticationClient.get_user_info("a-token")

        assert info.email == "user@usp.br"

    def test_raises_403_when_neither_domain_nor_email_is_allowed(self) -> None:
        with (
            patch.object(CONFIG, "allowed_gmails_domains", ["other.br"]),
            patch.object(CONFIG, "allowed_gmails", []),
            patch(
                "server.services.auth.authentication_client.requests.get",
                return_value=make_response(
                    status_code=200, json_data=self._valid_payload
                ),
            ),
        ):
            with pytest.raises(HTTPException) as exc_info:
                AuthenticationClient.get_user_info("a-token")

        assert exc_info.value.status_code == 403

    def test_raises_401_when_google_rejects_the_token(self) -> None:
        with patch(
            "server.services.auth.authentication_client.requests.get",
            return_value=make_response(status_code=401, json_data={"error": "invalid"}),
        ):
            with pytest.raises(HTTPException) as exc_info:
                AuthenticationClient.get_user_info("bad-token")

        assert exc_info.value.status_code == 401


class TestExchangeAuthCodeForTokens:
    def test_returns_access_and_refresh_tokens_on_success(self) -> None:
        payload = {"access_token": "access-123", "refresh_token": "refresh-456"}
        with patch(
            "server.services.auth.authentication_client.requests.post",
            return_value=make_response(status_code=200, json_data=payload),
        ):
            access_token, refresh_token = (
                AuthenticationClient.exchange_auth_code_for_tokens("auth-code")
            )

        assert access_token == "access-123"
        assert refresh_token == "refresh-456"

    def test_returns_none_refresh_token_when_absent(self) -> None:
        payload = {"access_token": "access-123"}
        with patch(
            "server.services.auth.authentication_client.requests.post",
            return_value=make_response(status_code=200, json_data=payload),
        ):
            access_token, refresh_token = (
                AuthenticationClient.exchange_auth_code_for_tokens("auth-code")
            )

        assert access_token == "access-123"
        assert refresh_token is None

    def test_raises_401_when_no_access_token_is_returned(self) -> None:
        payload = {"error": "invalid_grant"}
        with patch(
            "server.services.auth.authentication_client.requests.post",
            return_value=make_response(status_code=400, json_data=payload),
        ):
            with pytest.raises(HTTPException) as exc_info:
                AuthenticationClient.exchange_auth_code_for_tokens("bad-code")

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == payload  # type: ignore[comparison-overlap]


class TestRefreshAccessToken:
    def test_returns_new_access_token_on_success(self) -> None:
        payload = {"access_token": "new-access-123"}
        with patch(
            "server.services.auth.authentication_client.requests.post",
            return_value=make_response(status_code=200, json_data=payload),
        ):
            assert (
                AuthenticationClient.refresh_access_token("refresh-token")
                == "new-access-123"
            )

    def test_raises_401_when_refresh_fails(self) -> None:
        payload = {"error": "invalid_grant"}
        with patch(
            "server.services.auth.authentication_client.requests.post",
            return_value=make_response(status_code=400, json_data=payload),
        ):
            with pytest.raises(HTTPException) as exc_info:
                AuthenticationClient.refresh_access_token("bad-refresh-token")

        assert exc_info.value.status_code == 401


class TestGoogleUnavailable:
    """Every outgoing call has a timeout, and a timeout or connection error
    becomes a 503 instead of hanging the worker thread or looking like a
    bad credential (401)."""

    def test_get_user_info_passes_a_timeout(self) -> None:
        with patch(
            "server.services.auth.authentication_client.requests.get",
            return_value=make_response(status_code=401, json_data={}),
        ) as fake_get:
            with pytest.raises(HTTPException):
                AuthenticationClient.get_user_info("a-token")

        assert fake_get.call_args.kwargs["timeout"] == GOOGLE_REQUEST_TIMEOUT_SECONDS

    def test_refresh_access_token_passes_a_timeout(self) -> None:
        with patch(
            "server.services.auth.authentication_client.requests.post",
            return_value=make_response(
                status_code=200, json_data={"access_token": "a"}
            ),
        ) as fake_post:
            AuthenticationClient.refresh_access_token("refresh-token")

        assert fake_post.call_args.kwargs["timeout"] == GOOGLE_REQUEST_TIMEOUT_SECONDS

    @pytest.mark.parametrize(
        "error", [requests.Timeout("slow"), requests.ConnectionError("down")]
    )
    def test_get_user_info_raises_503(self, error: Exception) -> None:
        with patch(
            "server.services.auth.authentication_client.requests.get",
            side_effect=error,
        ):
            with pytest.raises(AuthProviderUnavailable) as exc_info:
                AuthenticationClient.get_user_info("a-token")

        assert exc_info.value.status_code == 503

    def test_refresh_access_token_raises_503_on_timeout(self) -> None:
        with patch(
            "server.services.auth.authentication_client.requests.post",
            side_effect=requests.Timeout("slow"),
        ):
            with pytest.raises(AuthProviderUnavailable):
                AuthenticationClient.refresh_access_token("refresh-token")

    def test_exchange_auth_code_raises_503_on_timeout(self) -> None:
        with patch(
            "server.services.auth.authentication_client.requests.post",
            side_effect=requests.Timeout("slow"),
        ):
            with pytest.raises(AuthProviderUnavailable):
                AuthenticationClient.exchange_auth_code_for_tokens("auth-code")


class FakeRedis:
    def __init__(self, fail: bool = False) -> None:
        self.store: dict[str, bytes] = {}
        self.ttls: dict[str, int] = {}
        self.fail = fail

    def get(self, key: str) -> bytes | None:
        if self.fail:
            raise ConnectionError("down")
        return self.store.get(key)

    def set(self, key: str, value: bytes, ex: int) -> None:
        if self.fail:
            raise ConnectionError("down")
        self.store[key] = value
        self.ttls[key] = ex


class TestUserInfoCache:
    _valid_payload = TestGetUserInfo._valid_payload
    _GET = "server.services.auth.authentication_client.requests.get"

    @pytest.fixture
    def fake_redis(self, monkeypatch: pytest.MonkeyPatch) -> FakeRedis:
        redis = FakeRedis()
        monkeypatch.setattr(CONFIG, "testing", False)
        monkeypatch.setattr(CONFIG, "allowed_gmails_domains", ["usp.br"])
        monkeypatch.setattr(CONFIG, "allowed_gmails", [])
        monkeypatch.setattr(
            "server.services.auth.authentication_client.get_sync_redis", lambda: redis
        )
        return redis

    def test_a_valid_token_hits_google_once(self, fake_redis: FakeRedis) -> None:
        response = make_response(status_code=200, json_data=self._valid_payload)
        with patch(self._GET, return_value=response) as fake_get:
            first = AuthenticationClient.get_user_info("a-token")
            second = AuthenticationClient.get_user_info("a-token")

        assert fake_get.call_count == 1
        assert first == second
        assert list(fake_redis.ttls.values()) == [USER_INFO_CACHE_SECONDS]

    def test_the_cache_key_does_not_contain_the_token(
        self, fake_redis: FakeRedis
    ) -> None:
        response = make_response(status_code=200, json_data=self._valid_payload)
        with patch(self._GET, return_value=response):
            AuthenticationClient.get_user_info("a-secret-token")

        assert all("a-secret-token" not in key for key in fake_redis.store)

    def test_a_rejected_token_is_negatively_cached(self, fake_redis: FakeRedis) -> None:
        response = make_response(status_code=401, json_data={"error": "invalid"})
        with patch(self._GET, return_value=response) as fake_get:
            for _ in range(3):
                with pytest.raises(HTTPException) as exc_info:
                    AuthenticationClient.get_user_info("garbage")
                assert exc_info.value.status_code == 401

        assert fake_get.call_count == 1
        assert list(fake_redis.ttls.values()) == [INVALID_TOKEN_CACHE_SECONDS]

    def test_google_server_errors_are_not_cached(self, fake_redis: FakeRedis) -> None:
        response = make_response(status_code=500, json_data={})
        with patch(self._GET, return_value=response) as fake_get:
            for _ in range(2):
                with pytest.raises(HTTPException):
                    AuthenticationClient.get_user_info("a-token")

        assert fake_get.call_count == 2
        assert fake_redis.store == {}

    def test_allowlist_is_rechecked_on_a_cache_hit(
        self, fake_redis: FakeRedis, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        response = make_response(status_code=200, json_data=self._valid_payload)
        with patch(self._GET, return_value=response):
            AuthenticationClient.get_user_info("a-token")
            monkeypatch.setattr(CONFIG, "allowed_gmails_domains", ["other.br"])
            with pytest.raises(HTTPException) as exc_info:
                AuthenticationClient.get_user_info("a-token")

        assert exc_info.value.status_code == 403

    def test_fails_open_when_redis_is_down(
        self, fake_redis: FakeRedis, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        broken = FakeRedis(fail=True)
        monkeypatch.setattr(
            "server.services.auth.authentication_client.get_sync_redis", lambda: broken
        )
        response = make_response(status_code=200, json_data=self._valid_payload)
        with patch(self._GET, return_value=response):
            info = AuthenticationClient.get_user_info("a-token")

        assert info.email == "user@usp.br"
