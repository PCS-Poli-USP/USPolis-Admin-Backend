from collections.abc import Callable
from unittest.mock import MagicMock

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.cors import CORSMiddleware

from server.middlewares.partner_cors_middleware import PartnerCorsMiddleware

FIRST_PARTY = "https://uspolis.com.br"
PARTNER = "https://gremio.poli.usp.br"


def make_client(
    loader: MagicMock | None = None,
    cache_seconds: float = 0,
    clock: Callable[[], float] | None = None,
) -> tuple[TestClient, MagicMock]:
    """Same layering as server/app.py: PartnerCors outside CORSMiddleware."""
    loader = loader or MagicMock(return_value={PARTNER})
    app = FastAPI()
    public = APIRouter(tags=["Public"])
    private = APIRouter(tags=["Authenticated"])

    @public.get("/buildings")
    def buildings() -> dict[str, str]:
        return {"ok": "public"}

    @private.get("/users/me")
    def me() -> dict[str, str]:
        return {"ok": "private"}

    app.include_router(public)
    app.include_router(private)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[FIRST_PARTY],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        PartnerCorsMiddleware,
        origins_loader=loader,
        cache_seconds=cache_seconds,
        **({"clock": clock} if clock is not None else {}),
    )
    return TestClient(app), loader


def preflight(
    client: TestClient, origin: str, path: str = "/buildings", method: str = "GET"
) -> object:
    return client.options(
        path,
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": method,
            "Access-Control-Request-Headers": "x-api-key",
        },
    )


class TestPreflight:
    def test_partner_origin_gets_get_only_without_credentials(self) -> None:
        client, _ = make_client()

        response = preflight(client, PARTNER)

        assert response.status_code == 200  # type: ignore[attr-defined]
        headers = response.headers  # type: ignore[attr-defined]
        assert headers["access-control-allow-origin"] == PARTNER
        assert headers["access-control-allow-methods"] == "GET, HEAD"
        assert "X-API-Key" in headers["access-control-allow-headers"]
        assert "access-control-allow-credentials" not in headers

    @pytest.mark.parametrize(
        ("origin", "path", "method"),
        [
            ("https://evil.com", "/buildings", "GET"),
            (PARTNER, "/buildings", "POST"),
            (PARTNER, "/users/me", "GET"),
        ],
        ids=["unknown-origin", "write-method", "private-route"],
    )
    def test_anything_else_is_refused_by_the_inner_cors(
        self, origin: str, path: str, method: str
    ) -> None:
        client, _ = make_client()

        response = preflight(client, origin, path, method)

        assert response.status_code == 400  # type: ignore[attr-defined]
        assert "access-control-allow-origin" not in response.headers  # type: ignore[attr-defined]


class TestActualRequests:
    def test_partner_response_is_readable_but_never_credentialed(self) -> None:
        client, _ = make_client()

        response = client.get("/buildings", headers={"Origin": PARTNER})

        assert response.headers["access-control-allow-origin"] == PARTNER
        assert "Origin" in response.headers["vary"]
        assert (
            "X-RateLimit-Remaining" in response.headers["access-control-expose-headers"]
        )
        assert "access-control-allow-credentials" not in response.headers

    def test_first_party_keeps_credentialed_cors_and_skips_the_lookup(self) -> None:
        client, loader = make_client()

        response = client.get("/buildings", headers={"Origin": FIRST_PARTY})

        assert response.headers["access-control-allow-origin"] == FIRST_PARTY
        assert response.headers["access-control-allow-credentials"] == "true"
        loader.assert_not_called()

    def test_requests_without_origin_skip_the_lookup(self) -> None:
        client, loader = make_client()

        assert client.get("/buildings").status_code == 200
        loader.assert_not_called()

    def test_partner_on_a_private_route_gets_no_cors(self) -> None:
        client, _ = make_client()

        response = client.get("/users/me", headers={"Origin": PARTNER})

        assert "access-control-allow-origin" not in response.headers

    def test_partner_origin_matches_case_insensitively(self) -> None:
        client, _ = make_client()

        response = client.get("/buildings", headers={"Origin": PARTNER.upper()})

        assert response.headers["access-control-allow-origin"] == PARTNER.upper()


class TestOriginsCache:
    def test_loads_origins_once_per_cache_window(self) -> None:
        ticks = iter([100.0, 110.0, 200.0])
        client, loader = make_client(cache_seconds=30, clock=lambda: next(ticks))

        for _ in range(3):  # t=100 load, t=110 cached, t=200 expired -> reload
            client.get("/buildings", headers={"Origin": PARTNER})

        assert loader.call_count == 2

    def test_a_failing_lookup_fails_closed(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        log = MagicMock()
        monkeypatch.setattr("server.middlewares.partner_cors_middleware.logger", log)
        client, _ = make_client(loader=MagicMock(side_effect=RuntimeError("db down")))

        response = client.get("/buildings", headers={"Origin": PARTNER})

        assert response.status_code == 200
        assert "access-control-allow-origin" not in response.headers
        assert "db down" in log.error.call_args.args[0]
