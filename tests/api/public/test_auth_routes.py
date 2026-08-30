from unittest.mock import patch

from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.user_db_model import User
from server.repositories.user_session_repository import UserSessionRepository
from server.services.auth.auth_user_info import AuthUserInfo
from server.utils.must_be_int import must_be_int

URL_PREFIX = "/auth"
_PATCH_TARGET = "server.routes.public.auth_routes.AuthenticationClient"


def _auth_info_for(user: User) -> AuthUserInfo:
    return AuthUserInfo(
        email=user.email,
        email_verified=True,
        domain=user.email.split("@")[1],
        name=user.name,
        picture="https://example.com/pic.png",
        given_name=user.name,
        family_name="",
    )


class TestGetTokens:
    def test_returns_tokens_and_sets_a_session_cookie(
        self, public_client: TestClient, admin_user: User
    ) -> None:
        with (
            patch(
                f"{_PATCH_TARGET}.exchange_auth_code_for_tokens",
                return_value=("access-tok", "refresh-tok"),
            ),
            patch(
                f"{_PATCH_TARGET}.get_user_info",
                return_value=_auth_info_for(admin_user),
            ),
        ):
            response = public_client.get(
                f"{URL_PREFIX}/get-tokens", params={"auth_code": "irrelevant"}
            )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["access_token"] == "access-tok"
        assert body["refresh_token"] == "refresh-tok"
        assert response.cookies.get("session") is not None

    def test_returns_401_when_no_tokens_are_received(
        self, public_client: TestClient
    ) -> None:
        with patch(
            f"{_PATCH_TARGET}.exchange_auth_code_for_tokens",
            return_value=(None, None),
        ):
            response = public_client.get(
                f"{URL_PREFIX}/get-tokens", params={"auth_code": "irrelevant"}
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRefreshToken:
    def test_returns_a_new_access_token_and_sets_a_session_cookie(
        self, public_client: TestClient, admin_user: User
    ) -> None:
        with (
            patch(
                f"{_PATCH_TARGET}.refresh_access_token",
                return_value="new-access-tok",
            ),
            patch(
                f"{_PATCH_TARGET}.get_user_info",
                return_value=_auth_info_for(admin_user),
            ),
        ):
            response = public_client.get(
                f"{URL_PREFIX}/refresh-token", params={"refresh_token": "irrelevant"}
            )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["access_token"] == "new-access-tok"
        assert response.cookies.get("session") is not None

    def test_raises_401_for_an_invalid_refresh_token(
        self, public_client: TestClient
    ) -> None:
        with patch(
            f"{_PATCH_TARGET}.refresh_access_token",
            side_effect=HTTPException(status.HTTP_401_UNAUTHORIZED, "expired"),
        ):
            response = public_client.get(
                f"{URL_PREFIX}/refresh-token", params={"refresh_token": "irrelevant"}
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid refresh token"


class TestLogout:
    def test_deletes_an_existing_session_and_clears_the_cookie(
        self, public_client: TestClient, admin_user: User, session: Session
    ) -> None:
        user_session = UserSessionRepository.create_session(
            user_id=must_be_int(admin_user.id),
            user_agent="pytest-agent",
            ip_address="127.0.0.1",
            session=session,
        )
        session.commit()
        public_client.cookies.set("session", user_session.id)

        response = public_client.post(f"{URL_PREFIX}/logout")

        assert response.status_code == status.HTTP_200_OK
        assert UserSessionRepository.get_session_opt(
            id=user_session.id, session=session
        ) is None

    def test_logout_without_a_session_cookie_still_succeeds(
        self, public_client: TestClient
    ) -> None:
        response = public_client.post(f"{URL_PREFIX}/logout")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Usuário deslogado com sucesso!"
