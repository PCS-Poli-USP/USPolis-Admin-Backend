from unittest.mock import patch

import pytest

from server.config import CONFIG
from server.utils.google_auth_utils import authenticate_with_google


def test_returns_id_info_when_domain_is_allowed() -> None:
    id_info = {"hd": "usp.br", "email_verified": True, "email": "user@usp.br"}
    with (
        patch.object(CONFIG, "allowed_gmails_domains", ["usp.br"]),
        patch(
            "server.utils.google_auth_utils.id_token.verify_oauth2_token",
            return_value=id_info,
        ),
    ):
        assert authenticate_with_google("a-token") == id_info


def test_raises_when_domain_is_not_allowed_and_email_is_verified() -> None:
    id_info = {"hd": "other.br", "email_verified": True, "email": "user@other.br"}
    with (
        patch.object(CONFIG, "allowed_gmails_domains", ["usp.br"]),
        patch(
            "server.utils.google_auth_utils.id_token.verify_oauth2_token",
            return_value=id_info,
        ),
    ):
        with pytest.raises(ValueError, match="Wrong domain name"):
            authenticate_with_google("a-token")


def test_raises_when_domain_is_not_allowed_and_email_is_unverified() -> None:
    id_info = {"hd": "other.br", "email_verified": False, "email": "user@other.br"}
    with (
        patch.object(CONFIG, "allowed_gmails_domains", ["usp.br"]),
        patch(
            "server.utils.google_auth_utils.id_token.verify_oauth2_token",
            return_value=id_info,
        ),
    ):
        with pytest.raises(ValueError, match="Wrong domain name"):
            authenticate_with_google("a-token")


def test_raises_when_domain_is_allowed_but_email_is_unverified() -> None:
    # A verified email is required even on an allowed domain - the domain
    # check alone must not be enough to let an unverified account through.
    id_info = {"hd": "usp.br", "email_verified": False, "email": "user@usp.br"}
    with (
        patch.object(CONFIG, "allowed_gmails_domains", ["usp.br"]),
        patch(
            "server.utils.google_auth_utils.id_token.verify_oauth2_token",
            return_value=id_info,
        ),
    ):
        with pytest.raises(ValueError, match="Wrong domain name"):
            authenticate_with_google("a-token")
