from dataclasses import replace
from datetime import timedelta
from unittest.mock import MagicMock

import pytest
from fakeredis import FakeAsyncRedis, FakeServer
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.testclient import TestClient
from starlette.datastructures import URL

from server.middlewares.api_key_middleware import (
    AUTH_FAILURE_LIMIT,
    ApiKeyMiddleware,
    matched_route_is_public,
)
from server.middlewares.logger_middleware import LoggerMessage, LoggerMiddleware
from server.middlewares.rate_limit_middleware import RateLimitMiddleware
from server.services.rate_limiter import (
    FixedWindowRateLimiter,
    RateLimitMode,
    RateLimitRule,
)
from server.services.security.api_key_auth import (
    INVALID_KEY_DETAIL,
    ApiKeyAuthenticator,
    ApiKeyRecord,
)
from server.services.security.api_key_crypto import generate_api_key
from server.utils.brazil_datetime import BrazilDatetime

ANON_RULES = [RateLimitRule(2, 60)]
NOW = 1_800_000_000 - 1_800_000_000 % 60
ORIGIN = "https://gremio.poli.usp.br"


def make_record(**overrides: object) -> tuple[ApiKeyRecord, str]:
    generated = generate_api_key()
    record = ApiKeyRecord(
        id=7,
        public_id=generated.public_id,
        client_id=3,
        key_hash=generated.key_hash,
        hash_version=generated.hash_version,
        allowed_path_prefixes=["/buildings"],
        allowed_origins=[],
        expires_at=BrazilDatetime.now_utc() + timedelta(days=30),
        revoked=False,
        client_active=True,
        rules=[RateLimitRule(5, 60)],
    )
    return replace(record, **overrides), generated.plaintext  # type: ignore[arg-type]


class Harness:
    """The production middleware order (ApiKey outside RateLimit) around a
    tiny app with one public and one authenticated route."""

    def __init__(self, *records: ApiKeyRecord, client_ip: str = "143.107.1.1") -> None:
        self.redis = FakeAsyncRedis()
        self.records = {r.public_id: r for r in records}
        self.last_used = MagicMock()
        app = FastAPI()
        public = APIRouter(tags=["Public"])
        private = APIRouter(tags=["Authenticated"])

        @public.get("/buildings")
        def buildings() -> dict[str, str]:
            return {"ok": "public"}

        @public.post("/buildings")
        def create_building() -> dict[str, str]:
            return {"ok": "public write"}

        @private.get("/users/me")
        def me() -> dict[str, str]:
            return {"ok": "private"}

        app.include_router(public)
        app.include_router(private)
        app.add_middleware(
            RateLimitMiddleware,
            mode=RateLimitMode.ENFORCE,
            rules=ANON_RULES,
            limiter=FixedWindowRateLimiter(self.redis, clock=lambda: NOW),
        )
        app.add_middleware(
            ApiKeyMiddleware,
            authenticator=ApiKeyAuthenticator(self.records.get, self.redis),
            redis=self.redis,
            last_used_writer=self.last_used,
        )
        self.client = TestClient(app, client=(client_ip, 50000))

    def get(self, path: str = "/buildings", **headers: str) -> object:
        return self.client.get(path, headers=headers)


def statuses(harness: Harness, n: int, **headers: str) -> list[int]:
    return [harness.get(**headers).status_code for _ in range(n)]  # type: ignore[attr-defined]


class TestAnonymous:
    def test_without_a_key_the_per_ip_limit_applies(self) -> None:
        assert statuses(Harness(), 3) == [200, 200, 429]

    def test_key_in_the_query_string_is_refused_even_without_header(self) -> None:
        response = Harness().client.get("/buildings?api_key=whatever")

        assert response.status_code == 400
        assert "X-API-Key" in response.json()["detail"]


class TestServerKey:
    def test_valid_key_uses_its_own_limit_not_the_ip_one(self) -> None:
        record, plaintext = make_record()
        harness = Harness(record)

        # Key allows 5/60s; anonymous IP limit is 2/60s.
        assert statuses(harness, 6, **{"X-API-Key": plaintext}) == [200] * 5 + [429]
        # Keyed requests didn't touch the IP bucket.
        assert harness.get().status_code == 200  # type: ignore[attr-defined]

    def test_out_of_scope_write_and_private_routes_are_403(self) -> None:
        record, plaintext = make_record()
        harness = Harness(record)
        headers = {"X-API-Key": plaintext}

        assert harness.client.post("/buildings", headers=headers).status_code == 403
        assert harness.client.get("/users/me", headers=headers).status_code == 403

    def test_last_used_is_written_once_per_window(self) -> None:
        record, plaintext = make_record()
        harness = Harness(record)

        statuses(harness, 3, **{"X-API-Key": plaintext})

        harness.last_used.assert_called_once_with(7)


class TestInvalidKey:
    def test_gets_a_generic_401_and_the_reason_only_in_the_log(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        record, plaintext = make_record(revoked=True)
        log = MagicMock()
        monkeypatch.setattr("server.middlewares.api_key_middleware.logger.warning", log)

        response = Harness(record).client.get(
            "/buildings", headers={"X-API-Key": plaintext}
        )

        assert response.status_code == 401
        assert response.json() == {"detail": INVALID_KEY_DETAIL}
        assert response.headers["WWW-Authenticate"] == "ApiKey"
        line = log.call_args.args[0]
        assert 'type="ApiKeyRejected"' in line and 'reason="revoked"' in line
        assert record.public_id in line
        assert plaintext not in line

    def test_does_not_fall_back_to_anonymous(self) -> None:
        response = Harness().client.get("/buildings", headers={"X-API-Key": "garbage"})

        assert response.status_code == 401

    def test_redis_down_still_rejects_without_crashing(self) -> None:
        server = FakeServer()
        server.connected = False
        app = FastAPI()

        @app.get("/buildings", tags=["Public"])
        def buildings() -> dict[str, str]:
            return {"ok": "public"}

        app.add_middleware(
            ApiKeyMiddleware,
            authenticator=ApiKeyAuthenticator({}.get, None),
            redis=FakeAsyncRedis(server=server),
        )
        client = TestClient(app)

        assert (
            client.get("/buildings", headers={"X-API-Key": "garbage"}).status_code
            == 401
        )

    def test_repeated_failures_from_an_ip_are_cut_off_with_429(self) -> None:
        harness = Harness()
        codes = statuses(harness, AUTH_FAILURE_LIMIT + 2, **{"X-API-Key": "garbage"})

        assert codes[:AUTH_FAILURE_LIMIT] == [401] * AUTH_FAILURE_LIMIT
        assert codes[AUTH_FAILURE_LIMIT:] == [429, 429]


class TestBrowserKey:
    def test_needs_an_allowed_origin(self) -> None:
        record, plaintext = make_record(allowed_origins=[ORIGIN])
        harness = Harness(record)

        ok = harness.get(**{"X-API-Key": plaintext, "Origin": ORIGIN})
        other = harness.get(**{"X-API-Key": plaintext, "Origin": "https://evil.com"})

        assert ok.status_code == 200  # type: ignore[attr-defined]
        assert other.status_code == 403  # type: ignore[attr-defined]

    def test_the_keys_own_limit_applies_first(self) -> None:
        record, plaintext = make_record(
            allowed_origins=[ORIGIN], rules=[RateLimitRule(1, 60)]
        )
        harness = Harness(record)
        headers = {"X-API-Key": plaintext, "Origin": ORIGIN}

        harness.get(**headers)
        blocked = harness.get(**headers)

        assert blocked.status_code == 429  # type: ignore[attr-defined]
        assert blocked.headers["X-RateLimit-Limit"] == "1"  # type: ignore[attr-defined]

    def test_each_visitor_also_keeps_the_per_ip_limit(self) -> None:
        # The key allows 5/60s, but one visitor (one IP) still gets 2/60s.
        record, plaintext = make_record(allowed_origins=[ORIGIN])
        harness = Harness(record)

        codes = statuses(harness, 3, **{"X-API-Key": plaintext, "Origin": ORIGIN})

        assert codes == [200, 200, 429]


def test_options_preflight_passes_untouched() -> None:
    response = Harness().client.options("/buildings", headers={"X-API-Key": "garbage"})

    assert response.status_code != 401


class TestMatchedRouteIsPublic:
    @pytest.fixture
    def app(self) -> FastAPI:
        return Harness().client.app  # type: ignore[return-value]

    def scope(self, app: FastAPI, path: str, method: str = "GET") -> dict:
        return {
            "type": "http",
            "path": path,
            "method": method,
            "app": app,
            "root_path": "",
        }

    @pytest.mark.parametrize(
        ("path", "method", "expected"),
        [
            ("/buildings", "GET", True),
            ("/users/me", "GET", False),
            ("/buildings", "DELETE", True),
            ("/nowhere", "GET", None),
        ],
        ids=["public", "authenticated", "method-mismatch", "no-route"],
    )
    def test_classifies_the_route(
        self, app: FastAPI, path: str, method: str, expected: bool | None
    ) -> None:
        assert matched_route_is_public(self.scope(app, path, method)) is expected


class TestLogging:
    def test_a_key_in_a_logged_url_is_redacted(self) -> None:
        _, plaintext = make_record()
        message = LoggerMessage(
            method="GET",
            url=URL(f"http://x/buildings?api_key={plaintext}&page=2"),
            type="Request",
        )

        line = str(message)

        assert plaintext not in line
        assert "[REDACTED_API_KEY]&page=2" in line

    def test_persisted_errors_record_which_key_made_the_request(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        record, plaintext = make_record()
        create = MagicMock()
        monkeypatch.setattr(
            "server.middlewares.logger_middleware.CONFIG.testing", False
        )
        monkeypatch.setattr("server.middlewares.logger_middleware.Session", MagicMock())
        monkeypatch.setattr(
            "server.middlewares.logger_middleware.logger.info", MagicMock()
        )
        monkeypatch.setattr(
            "server.middlewares.logger_middleware.loki_access_logger.info", MagicMock()
        )
        monkeypatch.setattr(
            "server.middlewares.logger_middleware.ApiAccessLogRepository.create", create
        )
        app = FastAPI()
        public = APIRouter(tags=["Public"])

        @public.get("/buildings")
        def conflict() -> None:
            raise HTTPException(status_code=409, detail="conflito")

        app.include_router(public)
        app.add_middleware(
            ApiKeyMiddleware,
            authenticator=ApiKeyAuthenticator({record.public_id: record}.get, None),
        )
        app.add_middleware(LoggerMiddleware)

        response = TestClient(app).get("/buildings", headers={"X-API-Key": plaintext})

        assert response.status_code == 409
        create.assert_called_once()
        assert create.call_args.kwargs["api_key_id"] == 7
