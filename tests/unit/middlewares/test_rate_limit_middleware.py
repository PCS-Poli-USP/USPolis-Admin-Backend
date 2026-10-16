import asyncio
from unittest.mock import MagicMock

import pytest
from fakeredis import FakeAsyncRedis, FakeServer
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.cors import CORSMiddleware

from server.middlewares import LoggerMiddleware, RateLimitMiddleware, app_path
from server.services.rate_limiter import (
    FixedWindowRateLimiter,
    RateLimitMode,
    RateLimitRule,
)

RULES = [RateLimitRule(2, 60)]
# Start of a 60s window: a real clock could cross a window edge mid-test
# and reset the counters.
NOW = 1_800_000_000 - 1_800_000_000 % 60


def fake_limiter(redis: FakeAsyncRedis | None = None) -> FixedWindowRateLimiter:
    return FixedWindowRateLimiter(
        redis if redis is not None else FakeAsyncRedis(), clock=lambda: NOW
    )


def make_client(
    mode: RateLimitMode,
    redis: FakeAsyncRedis | None = None,
    client_ip: str = "143.107.1.1",
) -> TestClient:
    app = FastAPI()

    @app.get("/classrooms")
    def classrooms() -> dict[str, str]:
        return {"ok": "yes"}

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"ok": "yes"}

    limiter = fake_limiter(redis)
    app.add_middleware(RateLimitMiddleware, mode=mode, rules=RULES, limiter=limiter)
    return TestClient(app, client=(client_ip, 50000))


class TestEnforceMode:
    def test_blocks_after_the_limit_with_429_and_retry_after(self) -> None:
        client = make_client(RateLimitMode.ENFORCE)
        statuses = [client.get("/classrooms").status_code for _ in range(3)]

        assert statuses == [200, 200, 429]
        blocked = client.get("/classrooms")
        assert blocked.status_code == 429
        assert 0 < int(blocked.headers["Retry-After"]) <= 60
        assert blocked.headers["X-RateLimit-Remaining"] == "0"
        assert "Muitas requisições" in blocked.json()["detail"]

    def test_allowed_responses_carry_rate_limit_headers(self) -> None:
        response = make_client(RateLimitMode.ENFORCE).get("/classrooms")

        assert response.headers["X-RateLimit-Limit"] == "2"
        assert response.headers["X-RateLimit-Remaining"] == "1"

    def test_each_ip_has_its_own_budget(self) -> None:
        redis = FakeAsyncRedis()
        first = make_client(RateLimitMode.ENFORCE, redis, client_ip="1.1.1.1")
        second = make_client(RateLimitMode.ENFORCE, redis, client_ip="2.2.2.2")
        for _ in range(2):
            first.get("/classrooms")

        assert first.get("/classrooms").status_code == 429
        assert second.get("/classrooms").status_code == 200

    def test_forwarded_for_header_does_not_change_the_bucket(self) -> None:
        client = make_client(RateLimitMode.ENFORCE)
        statuses = [
            client.get(
                "/classrooms", headers={"x-forwarded-for": f"10.0.0.{i}"}
            ).status_code
            for i in range(3)
        ]

        assert statuses == [200, 200, 429]

    def test_exempt_paths_are_never_limited(self) -> None:
        client = make_client(RateLimitMode.ENFORCE)

        assert all(client.get("/health").status_code == 200 for _ in range(5))

    def test_options_requests_are_not_counted(self) -> None:
        client = make_client(RateLimitMode.ENFORCE)
        for _ in range(5):
            client.options("/classrooms")

        assert client.get("/classrooms").status_code == 200


class TestShadowMode:
    def test_lets_requests_through_and_logs_once(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        fake_warning = MagicMock()
        monkeypatch.setattr("server.middlewares.logger.warning", fake_warning)
        client = make_client(RateLimitMode.SHADOW)
        statuses = [client.get("/classrooms").status_code for _ in range(5)]

        assert statuses == [200] * 5
        fake_warning.assert_called_once()
        line = fake_warning.call_args.args[0]
        assert 'type="RateLimit"' in line
        assert 'mode="shadow"' in line
        assert 'rule="2/60"' in line
        assert 'host="143.107.1.1"' in line

    def test_does_not_add_rate_limit_headers(self) -> None:
        response = make_client(RateLimitMode.SHADOW).get("/classrooms")

        assert "X-RateLimit-Limit" not in response.headers


class TestOffAndFailOpen:
    def test_off_mode_never_touches_redis(self) -> None:
        redis = FakeAsyncRedis()
        client = make_client(RateLimitMode.OFF, redis)

        assert all(client.get("/classrooms").status_code == 200 for _ in range(5))
        assert asyncio.run(redis.keys("*")) == []

    @pytest.mark.parametrize(
        ("mode", "limits"),
        [("block-everything", "40/10"), ("enforce", "40 per minute")],
    )
    def test_invalid_config_fails_open_instead_of_breaking_requests(
        self, monkeypatch: pytest.MonkeyPatch, mode: str, limits: str
    ) -> None:
        monkeypatch.setattr("server.middlewares.CONFIG.testing", False)
        monkeypatch.setattr("server.middlewares.CONFIG.rate_limit_mode", mode)
        monkeypatch.setattr("server.middlewares.CONFIG.anon_rate_limits", limits)
        fake_error = MagicMock()
        monkeypatch.setattr("server.middlewares.logger.error", fake_error)
        app = FastAPI()

        @app.get("/classrooms")
        def classrooms() -> dict[str, str]:
            return {"ok": "yes"}

        app.add_middleware(RateLimitMiddleware, limiter=fake_limiter(FakeAsyncRedis()))
        client = TestClient(app)

        assert all(client.get("/classrooms").status_code == 200 for _ in range(3))
        assert "Invalid rate limit config" in fake_error.call_args.args[0]

    def test_test_suite_never_rate_limits_whatever_the_env_says(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # A developer's .env with RATE_LIMIT_MODE=enforce must not turn the
        # API tests into 429s.
        monkeypatch.setattr("server.middlewares.CONFIG.testing", True)
        monkeypatch.setattr("server.middlewares.CONFIG.rate_limit_mode", "enforce")
        monkeypatch.setattr("server.middlewares.CONFIG.anon_rate_limits", "1/60")
        app = FastAPI()

        @app.get("/classrooms")
        def classrooms() -> dict[str, str]:
            return {"ok": "yes"}

        app.add_middleware(RateLimitMiddleware, limiter=fake_limiter())
        client = TestClient(app)

        assert all(client.get("/classrooms").status_code == 200 for _ in range(3))

    def test_builds_the_limiter_from_get_redis_on_first_request(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "server.middlewares.get_redis", MagicMock(return_value=FakeAsyncRedis())
        )
        # Same class, fixed clock: the window can't roll over mid-test.
        monkeypatch.setattr(
            "server.middlewares.FixedWindowRateLimiter",
            lambda redis: FixedWindowRateLimiter(redis, clock=lambda: NOW),
        )
        app = FastAPI()

        @app.get("/classrooms")
        def classrooms() -> dict[str, str]:
            return {"ok": "yes"}

        app.add_middleware(RateLimitMiddleware, mode=RateLimitMode.ENFORCE, rules=RULES)
        client = TestClient(app)
        statuses = [client.get("/classrooms").status_code for _ in range(3)]

        assert statuses == [200, 200, 429]

    def test_without_redis_configured_requests_pass(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "server.middlewares.get_redis", MagicMock(return_value=None)
        )
        app = FastAPI()

        @app.get("/classrooms")
        def classrooms() -> dict[str, str]:
            return {"ok": "yes"}

        app.add_middleware(RateLimitMiddleware, mode=RateLimitMode.ENFORCE, rules=RULES)
        client = TestClient(app)

        assert all(client.get("/classrooms").status_code == 200 for _ in range(5))

    def test_redis_down_fails_open(self) -> None:
        server = FakeServer()
        server.connected = False
        client = make_client(RateLimitMode.ENFORCE, FakeAsyncRedis(server=server))

        assert all(client.get("/classrooms").status_code == 200 for _ in range(5))


def test_429_keeps_cors_headers_with_the_app_middleware_order() -> None:
    # Same order as server/app.py: RateLimit added before CORS, so CORS wraps
    # it and the browser sees a readable 429 instead of a CORS error.
    app = FastAPI()

    @app.get("/classrooms")
    def classrooms() -> dict[str, str]:
        return {"ok": "yes"}

    limiter = fake_limiter(FakeAsyncRedis())
    app.add_middleware(
        RateLimitMiddleware, mode=RateLimitMode.ENFORCE, rules=RULES, limiter=limiter
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://uspolis.com.br"],
        expose_headers=["Retry-After"],
    )
    client = TestClient(app, client=("143.107.1.1", 50000))
    origin = {"Origin": "https://uspolis.com.br"}
    for _ in range(2):
        client.get("/classrooms", headers=origin)

    blocked = client.get("/classrooms", headers=origin)
    assert blocked.status_code == 429
    assert blocked.headers["access-control-allow-origin"] == "https://uspolis.com.br"
    assert "Retry-After" in blocked.headers["access-control-expose-headers"]


class TestAppPath:
    @pytest.mark.parametrize(
        ("path", "root_path", "expected"),
        [
            ("/classrooms", "/api", "/classrooms"),
            ("/api/classrooms", "/api", "/classrooms"),
            ("/api", "/api", "/"),
            ("/apiary", "/api", "/apiary"),
            ("/health", "", "/health"),
        ],
    )
    def test_strips_only_the_root_path_prefix(
        self, path: str, root_path: str, expected: str
    ) -> None:
        assert app_path({"path": path, "root_path": root_path}) == expected


class TestRateLimitEventPersistence:
    """Only the first rate-limited request per IP and window reaches
    `apiaccesslog`, so the limits can be tuned without a DB write per 429."""

    @pytest.fixture
    def create_log(self, monkeypatch: pytest.MonkeyPatch) -> MagicMock:
        monkeypatch.setattr("server.middlewares.CONFIG.testing", False)
        monkeypatch.setattr("server.middlewares.Session", MagicMock())
        monkeypatch.setattr("server.middlewares.logger.info", MagicMock())
        monkeypatch.setattr("server.middlewares.loki_access_logger.info", MagicMock())
        create = MagicMock()
        monkeypatch.setattr("server.middlewares.ApiAccessLogRepository.create", create)
        return create

    def make_logged_client(self, mode: RateLimitMode) -> TestClient:
        app = FastAPI()

        @app.get("/classrooms", tags=["Public"])
        def classrooms() -> dict[str, str]:
            return {"ok": "yes"}

        limiter = fake_limiter(FakeAsyncRedis())
        app.add_middleware(RateLimitMiddleware, mode=mode, rules=RULES, limiter=limiter)
        app.add_middleware(LoggerMiddleware)
        return TestClient(app, client=("143.107.1.1", 50000))

    def test_enforce_persists_only_the_first_429(self, create_log: MagicMock) -> None:
        client = self.make_logged_client(RateLimitMode.ENFORCE)
        statuses = [client.get("/classrooms").status_code for _ in range(6)]

        assert statuses == [200, 200, 429, 429, 429, 429]
        create_log.assert_called_once()
        row = create_log.call_args.kwargs
        assert row["status_code"] == 429
        assert row["endpoint"] == "/classrooms"
        assert row["ip_address"] == "143.107.1.1"
        assert "RateLimit" in row["tags"] and "RateLimit:enforce" in row["tags"]
        assert "regra 2/60" in row["detail"]

    def test_shadow_persists_the_would_be_429_once(self, create_log: MagicMock) -> None:
        client = self.make_logged_client(RateLimitMode.SHADOW)
        statuses = [client.get("/classrooms").status_code for _ in range(6)]

        assert statuses == [200] * 6
        create_log.assert_called_once()
        row = create_log.call_args.kwargs
        assert row["status_code"] == 429
        assert "RateLimit:shadow" in row["tags"]
        assert "Public" in row["tags"]  # route matched, since nothing was blocked
        assert "não bloqueada" in row["detail"]

    def test_requests_within_the_limit_are_not_persisted(
        self, create_log: MagicMock
    ) -> None:
        client = self.make_logged_client(RateLimitMode.ENFORCE)
        for _ in range(2):
            client.get("/classrooms")

        create_log.assert_not_called()
