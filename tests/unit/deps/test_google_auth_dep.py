from unittest.mock import patch

import pytest
from fastapi import HTTPException

from server.deps.google_auth_dep import (
    google_authorization_authenticate,
    google_id_token_authenticate,
)

_PATCH_TARGET = "server.deps.google_auth_dep.authenticate_with_google"


class TestGoogleIdTokenAuthenticate:
    def test_returns_authenticate_with_google_result(self) -> None:
        id_info = {"sub": "123"}
        with patch(_PATCH_TARGET, return_value=id_info):
            assert google_id_token_authenticate("a-token") == id_info

    def test_raises_401_when_authenticate_with_google_raises(self) -> None:
        with patch(_PATCH_TARGET, side_effect=ValueError("Wrong domain name.")):
            with pytest.raises(HTTPException) as exc_info:
                google_id_token_authenticate("bad-token")

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Wrong domain name."


class TestGoogleAuthorizationAuthenticate:
    def test_returns_authenticate_with_google_result(self) -> None:
        id_info = {"sub": "123"}
        with patch(_PATCH_TARGET, return_value=id_info):
            assert google_authorization_authenticate("a-token") == id_info

    def test_raises_401_when_authenticate_with_google_raises(self) -> None:
        with patch(_PATCH_TARGET, side_effect=ValueError("Wrong number of segments")):
            with pytest.raises(HTTPException) as exc_info:
                google_authorization_authenticate("bad-token")

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Wrong number of segments"
