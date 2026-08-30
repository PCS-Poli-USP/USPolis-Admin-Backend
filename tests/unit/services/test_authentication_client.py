from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from server.config import CONFIG
from server.services.auth.authentication_client import AuthenticationClient


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
                return_value=make_response(status_code=200, json_data=self._valid_payload),
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
                return_value=make_response(status_code=200, json_data=self._valid_payload),
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
                return_value=make_response(status_code=200, json_data=self._valid_payload),
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
