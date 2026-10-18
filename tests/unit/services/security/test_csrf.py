from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi import Request

from server.config import CONFIG
from server.deps.authenticate import (
    authenticate_from_cookie,
    public_authenticate_from_cookie,
)
from server.services.security.csrf import (
    UntrustedOriginForCookie,
    is_trusted_cookie_request,
    request_origin,
)


def make_request(
    method: str = "POST", headers: dict[str, str] | None = None
) -> Request:
    scope: dict[str, Any] = {
        "type": "http",
        "method": method,
        "path": "/classrooms",
        "headers": [
            (key.lower().encode(), value.encode())
            for key, value in {"host": "uspolis.com.br", **(headers or {})}.items()
        ],
    }
    return Request(scope)


@pytest.fixture(autouse=True)
def allowed_origins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        CONFIG, "allowed_origins", ["https://uspolis.com.br", "https://localhost:3000"]
    )


class TestIsTrustedCookieRequest:
    @pytest.mark.parametrize("method", ["GET", "HEAD", "OPTIONS"])
    def test_safe_methods_are_not_checked(self, method: str) -> None:
        request = make_request(method, {"origin": "https://evil.example"})
        assert is_trusted_cookie_request(request)

    @pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
    def test_rejects_a_foreign_origin(self, method: str) -> None:
        request = make_request(method, {"origin": "https://evil.example"})
        assert not is_trusted_cookie_request(request)

    def test_accepts_an_allowed_origin(self) -> None:
        # Dev: frontend and API on different origins.
        request = make_request(headers={"origin": "https://localhost:3000"})
        assert is_trusted_cookie_request(request)

    def test_accepts_a_same_origin_host_not_in_the_list(self) -> None:
        request = make_request(
            headers={
                "host": "www.uspolis.com.br",
                "origin": "https://www.uspolis.com.br",
            }
        )
        assert is_trusted_cookie_request(request)

    def test_rejects_a_sibling_subdomain(self) -> None:
        """Same *site* for SameSite purposes, so only this check stops it."""
        request = make_request(headers={"origin": "https://blog.uspolis.com.br"})
        assert not is_trusted_cookie_request(request)

    def test_rejects_a_missing_origin(self) -> None:
        assert not is_trusted_cookie_request(make_request())

    def test_rejects_a_null_origin(self) -> None:
        assert not is_trusted_cookie_request(make_request(headers={"origin": "null"}))

    def test_falls_back_to_the_referer(self) -> None:
        good = make_request(
            headers={"referer": "https://uspolis.com.br/allocation?x=1"}
        )
        bad = make_request(headers={"referer": "https://evil.example/page"})
        assert is_trusted_cookie_request(good)
        assert not is_trusted_cookie_request(bad)

    def test_origin_wins_over_referer(self) -> None:
        request = make_request(
            headers={
                "origin": "https://evil.example",
                "referer": "https://uspolis.com.br/",
            }
        )
        assert request_origin(request) == "https://evil.example"
        assert not is_trusted_cookie_request(request)


class TestCookieAuthDependencies:
    def test_required_auth_rejects_a_cross_origin_cookie_request(self) -> None:
        request = make_request(
            headers={"origin": "https://evil.example", "cookie": "session=abc"}
        )
        db = MagicMock()

        with pytest.raises(UntrustedOriginForCookie) as exc_info:
            authenticate_from_cookie(request=request, session=db)

        assert exc_info.value.status_code == 403
        db.exec.assert_not_called()  # rejected before touching the database

    def test_public_auth_serves_a_cross_origin_cookie_request_anonymously(
        self,
    ) -> None:
        request = make_request(
            headers={"origin": "https://evil.example", "cookie": "session=abc"}
        )
        db = MagicMock()

        public_authenticate_from_cookie(request=request, session=db)

        assert getattr(request.state, "current_user", None) is None
        db.exec.assert_not_called()
