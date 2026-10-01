from typing import Any
from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.mobile_user_db_model import MobileUser
from tests.utils.mobile_user_test_utils import make_mobile_user

URL_PREFIX = "/mobile/authentication"

FAKE_ID_INFO: dict[str, Any] = {
    "sub": "google-sub-123",
    "given_name": "Ana",
    "family_name": "Silva",
    "email": "ana@usp.br",
    "picture": "https://example.com/pic.png",
    "email_verified": True,
    "hd": "usp.br",
}

_PATCH_TARGET = "server.deps.google_auth_dep.authenticate_with_google"


class TestAuthenticateUser:
    def test_returns_registered_user_when_sub_exists(
        self, public_client: TestClient, session: Session
    ) -> None:
        make_mobile_user(
            sub=FAKE_ID_INFO["sub"], email=FAKE_ID_INFO["email"], session=session
        )

        with patch(_PATCH_TARGET, return_value=FAKE_ID_INFO):
            response = public_client.post(
                URL_PREFIX, headers={"idToken": "irrelevant-mocked-token"}
            )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["is_registered_user"] is True
        assert body["user"]["sub"] == FAKE_ID_INFO["sub"]
        assert body["user"]["email"] == FAKE_ID_INFO["email"]

    def test_returns_not_registered_when_sub_does_not_exist(
        self, public_client: TestClient
    ) -> None:
        # No MobileUser created for this sub.
        with patch(_PATCH_TARGET, return_value=FAKE_ID_INFO):
            response = public_client.post(
                URL_PREFIX, headers={"idToken": "irrelevant-mocked-token"}
            )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["is_registered_user"] is False
        assert body["user"] is None

    def test_returns_401_for_invalid_token(self, public_client: TestClient) -> None:
        with patch(_PATCH_TARGET, side_effect=ValueError("Wrong number of segments")):
            response = public_client.post(
                URL_PREFIX, headers={"idToken": "not-a-real-token"}
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_returns_401_when_domain_is_not_allowed(
        self, public_client: TestClient
    ) -> None:
        with patch(_PATCH_TARGET, side_effect=ValueError("Wrong domain name.")):
            response = public_client.post(
                URL_PREFIX, headers={"idToken": "some-token"}
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_requires_idtoken_header(self, public_client: TestClient) -> None:
        response = public_client.post(URL_PREFIX)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCreateNewUser:
    def test_creates_and_returns_a_new_user(
        self, public_client: TestClient, session: Session
    ) -> None:
        with patch(_PATCH_TARGET, return_value=FAKE_ID_INFO):
            response = public_client.post(
                f"{URL_PREFIX}/new-user", headers={"idToken": "irrelevant-mocked-token"}
            )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["is_registered_user"] is True
        assert body["user"]["sub"] == FAKE_ID_INFO["sub"]
        assert body["user"]["given_name"] == FAKE_ID_INFO["given_name"]
        assert body["user"]["family_name"] == FAKE_ID_INFO["family_name"]
        assert body["user"]["email"] == FAKE_ID_INFO["email"]

        persisted = session.get(MobileUser, body["user"]["id"])
        assert persisted is not None
        assert persisted.sub == FAKE_ID_INFO["sub"]

    def test_returns_401_for_invalid_token(self, public_client: TestClient) -> None:
        with patch(_PATCH_TARGET, side_effect=ValueError("Wrong number of segments")):
            response = public_client.post(
                f"{URL_PREFIX}/new-user", headers={"idToken": "not-a-real-token"}
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_returns_401_when_domain_is_not_allowed(
        self, public_client: TestClient
    ) -> None:
        with patch(_PATCH_TARGET, side_effect=ValueError("Wrong domain name.")):
            response = public_client.post(
                f"{URL_PREFIX}/new-user", headers={"idToken": "some-token"}
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_requires_idtoken_header(self, public_client: TestClient) -> None:
        response = public_client.post(f"{URL_PREFIX}/new-user")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
