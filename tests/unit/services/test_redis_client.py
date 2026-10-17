from collections.abc import Iterator
from unittest.mock import MagicMock

import pytest
from fakeredis import FakeAsyncRedis, FakeServer

from server.services import redis_client
from server.services.redis_client import (
    check_rate_limit_setup,
    get_redis,
    get_sync_redis,
    redact_url,
)

REDIS_URL = "redis://:s3cret@127.0.0.1:6379/0"


@pytest.fixture
def config(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Production-like config: rate limiting enforced, not testing."""
    monkeypatch.setattr("server.services.redis_client.CONFIG.testing", False)
    monkeypatch.setattr(
        "server.services.redis_client.CONFIG.rate_limit_mode", "enforce"
    )
    monkeypatch.setattr(
        "server.services.redis_client.CONFIG.anon_rate_limits", "40/10,150/60"
    )
    monkeypatch.setattr("server.services.redis_client.CONFIG.redis_url", REDIS_URL)
    monkeypatch.setattr(redis_client, "_redis", None)
    yield


@pytest.fixture
def log(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    fake_logger = MagicMock()
    monkeypatch.setattr("server.services.redis_client.logger", fake_logger)
    return fake_logger


class TestRedactUrl:
    def test_masks_the_password(self) -> None:
        assert redact_url(REDIS_URL) == "redis://:***@127.0.0.1:6379/0"

    def test_keeps_the_username(self) -> None:
        assert redact_url("redis://app:pw@redis:6379") == "redis://app:***@redis:6379"

    def test_url_without_password_is_unchanged(self) -> None:
        assert redact_url("redis://127.0.0.1:6379/0") == "redis://127.0.0.1:6379/0"


class TestGetRedis:
    def test_returns_none_without_url(
        self, config: None, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("server.services.redis_client.CONFIG.redis_url", "")

        assert get_redis() is None

    def test_sync_client_is_none_without_url(
        self, config: None, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("server.services.redis_client.CONFIG.redis_url", "")

        assert get_sync_redis() is None

    def test_sync_client_is_built_once(
        self, config: None, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(redis_client, "_sync_redis", None)
        first = get_sync_redis()

        assert first is not None
        assert get_sync_redis() is first

    def test_builds_one_client_per_process(self, config: None) -> None:
        # Building the client doesn't connect, so no Redis is needed here.
        first = get_redis()

        assert first is not None
        assert get_redis() is first


@pytest.mark.asyncio
class TestCheckRateLimitSetup:
    async def test_reports_ok_with_mode_and_rules_and_hides_the_password(
        self, config: None, log: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(redis_client, "_redis", FakeAsyncRedis())

        message = await check_rate_limit_setup()

        assert message.startswith("Rate limit: Redis OK at redis://:***@127.0.0.1")
        assert "mode=enforce" in message and "rules=40/10, 150/60" in message
        assert "s3cret" not in message
        log.info.assert_called_once_with(message)

    async def test_reports_unreachable_redis_as_error(
        self, config: None, log: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        server = FakeServer()
        server.connected = False
        monkeypatch.setattr(redis_client, "_redis", FakeAsyncRedis(server=server))

        message = await check_rate_limit_setup()

        assert "Redis unreachable" in message and "fail-open" in message
        assert "s3cret" not in message
        log.error.assert_called_once_with(message)

    async def test_reports_missing_redis_url_as_error(
        self, config: None, log: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("server.services.redis_client.CONFIG.redis_url", "")

        message = await check_rate_limit_setup()

        assert "REDIS_URL is empty" in message
        log.error.assert_called_once_with(message)

    async def test_reports_invalid_config_as_error(
        self, config: None, log: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "server.services.redis_client.CONFIG.rate_limit_mode", "block-all"
        )

        message = await check_rate_limit_setup()

        assert "invalid config" in message
        log.error.assert_called_once_with(message)

    async def test_off_mode_is_reported_without_touching_redis(
        self, config: None, log: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "server.services.redis_client.CONFIG.rate_limit_mode", "off"
        )
        get_redis_mock = MagicMock()
        monkeypatch.setattr("server.services.redis_client.get_redis", get_redis_mock)

        message = await check_rate_limit_setup()

        assert message == "Rate limit: disabled (RATE_LIMIT_MODE=off)"
        get_redis_mock.assert_not_called()

    async def test_testing_always_disables_rate_limiting(
        self, config: None, log: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("server.services.redis_client.CONFIG.testing", True)

        assert await check_rate_limit_setup() == "Rate limit: disabled (testing)"
