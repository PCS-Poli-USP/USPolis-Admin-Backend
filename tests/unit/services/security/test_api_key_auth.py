from dataclasses import replace
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
from fakeredis import FakeAsyncRedis, FakeRedis, FakeServer

from server.services.rate_limiter import RateLimitRule
from server.services.security import api_key_auth
from server.services.security.api_key_auth import (
    CACHE_PREFIX,
    FORBIDDEN_DETAIL,
    INVALID_KEY_DETAIL,
    ApiKeyAuthenticator,
    ApiKeyRecord,
    ApiKeyRejection,
    check_api_key_setup,
    invalidate_api_key_cache,
    should_write_last_used,
)
from server.services.security.api_key_crypto import generate_api_key

NOW = datetime(2026, 10, 17, 12, 0, 0)
RULES = [RateLimitRule(30, 10), RateLimitRule(120, 60)]


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
        expires_at=NOW + timedelta(days=30),
        revoked=False,
        client_active=True,
        rules=RULES,
    )
    return replace(record, **overrides), generated.plaintext  # type: ignore[arg-type]


class FakeLoader:
    """Stands in for the DB; counts lookups to prove the cache works."""

    def __init__(self, *records: ApiKeyRecord) -> None:
        self.records = {r.public_id: r for r in records}
        self.calls = 0

    def __call__(self, public_id: str) -> ApiKeyRecord | None:
        self.calls += 1
        return self.records.get(public_id)


def authenticator(
    loader: FakeLoader, redis: FakeAsyncRedis | None = None
) -> ApiKeyAuthenticator:
    return ApiKeyAuthenticator(loader, redis, clock=lambda: NOW)


async def authenticate(
    auth: ApiKeyAuthenticator,
    plaintext: str,
    *,
    method: str = "GET",
    path: str = "/buildings",
    origin: str | None = None,
    is_public_route: bool | None = True,
) -> object:
    return await auth.authenticate(
        plaintext,
        method=method,
        path=path,
        origin=origin,
        is_public_route=is_public_route,
    )


async def rejection(
    auth: ApiKeyAuthenticator, plaintext: str, **kwargs: object
) -> ApiKeyRejection:
    with pytest.raises(ApiKeyRejection) as error:
        await authenticate(auth, plaintext, **kwargs)  # type: ignore[arg-type]
    return error.value


@pytest.mark.asyncio
class TestValidKey:
    async def test_returns_the_identity_with_its_effective_limits(self) -> None:
        record, plaintext = make_record()

        identity = await authenticate(authenticator(FakeLoader(record)), plaintext)

        assert identity == api_key_auth.ApiKeyIdentity(
            key_id=7,
            public_id=record.public_id,
            client_id=3,
            rules=RULES,
            is_browser_key=False,
        )

    async def test_unmatched_route_in_scope_is_left_to_the_app_404(self) -> None:
        record, plaintext = make_record()

        await authenticate(
            authenticator(FakeLoader(record)),
            plaintext,
            path="/buildings/does-not-exist",
            is_public_route=None,
        )


@pytest.mark.asyncio
class TestInvalidKey:
    async def test_malformed_key_is_rejected_without_any_lookup(self) -> None:
        loader = FakeLoader()

        error = await rejection(authenticator(loader), "up_dev_not-a-key")

        assert error.status_code == 401
        assert loader.calls == 0

    async def test_unknown_key(self) -> None:
        _, plaintext = make_record()

        error = await rejection(authenticator(FakeLoader()), plaintext)

        assert (error.status_code, error.reason) == (401, "unknown public_id")

    async def test_wrong_secret_for_a_known_public_id(self) -> None:
        record, _ = make_record()
        _, other_plaintext = make_record()
        forged = replace(record, public_id=other_plaintext.split("_")[2])

        error = await rejection(authenticator(FakeLoader(forged)), other_plaintext)

        assert (error.status_code, error.reason) == (401, "hash mismatch")

    @pytest.mark.parametrize(
        ("overrides", "reason"),
        [
            ({"revoked": True}, "revoked"),
            ({"client_active": False}, "client inactive"),
            ({"expires_at": NOW}, "expired"),
        ],
    )
    async def test_unusable_keys_get_401(self, overrides: dict, reason: str) -> None:
        record, plaintext = make_record(**overrides)

        error = await rejection(authenticator(FakeLoader(record)), plaintext)

        assert (error.status_code, error.reason) == (401, reason)

    async def test_missing_server_secret_is_503(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        record, plaintext = make_record()
        monkeypatch.setattr(
            "server.services.security.api_key_crypto.CONFIG.api_key_secret", ""
        )

        error = await rejection(authenticator(FakeLoader(record)), plaintext)

        assert error.status_code == 503


@pytest.mark.asyncio
class TestPermissions:
    @pytest.mark.parametrize(
        ("kwargs", "reason"),
        [
            ({"method": "POST"}, "method POST not allowed"),
            ({"is_public_route": False}, "not a public route"),
            ({"path": "/classrooms"}, "path /classrooms out of scope"),
        ],
        ids=["write-method", "non-public-route", "out-of-scope"],
    )
    async def test_forbidden_requests_get_403(self, kwargs: dict, reason: str) -> None:
        record, plaintext = make_record()

        error = await rejection(authenticator(FakeLoader(record)), plaintext, **kwargs)

        assert (error.status_code, error.reason) == (403, reason)

    async def test_root_prefix_covers_every_public_path(self) -> None:
        record, plaintext = make_record(allowed_path_prefixes=["/"])

        await authenticate(
            authenticator(FakeLoader(record)), plaintext, path="/allocations/events"
        )

    async def test_server_key_used_from_a_browser_is_rejected(self) -> None:
        record, plaintext = make_record()

        error = await rejection(
            authenticator(FakeLoader(record)), plaintext, origin="https://evil.com"
        )

        assert (error.status_code, error.reason) == (
            403,
            "server key sent from a browser",
        )


@pytest.mark.asyncio
class TestBrowserKeys:
    ORIGIN = "https://gremio.poli.usp.br"

    async def test_allowed_origin_passes_case_insensitively(self) -> None:
        record, plaintext = make_record(allowed_origins=[self.ORIGIN])

        identity = await authenticate(
            authenticator(FakeLoader(record)),
            plaintext,
            origin="https://Gremio.Poli.USP.br",
        )

        assert identity.is_browser_key  # type: ignore[attr-defined]

    @pytest.mark.parametrize("origin", ["https://evil.com", None])
    async def test_other_or_missing_origin_is_rejected(
        self, origin: str | None
    ) -> None:
        record, plaintext = make_record(allowed_origins=[self.ORIGIN])

        error = await rejection(
            authenticator(FakeLoader(record)), plaintext, origin=origin
        )

        assert error.status_code == 403


@pytest.mark.asyncio
class TestCache:
    async def test_second_request_is_served_from_redis(self) -> None:
        record, plaintext = make_record()
        loader = FakeLoader(record)
        auth = authenticator(loader, FakeAsyncRedis())

        await authenticate(auth, plaintext)
        await authenticate(auth, plaintext)

        assert loader.calls == 1

    async def test_unknown_ids_are_cached_too(self) -> None:
        _, plaintext = make_record()
        loader = FakeLoader()
        auth = authenticator(loader, FakeAsyncRedis())

        for _ in range(3):
            await rejection(auth, plaintext)

        assert loader.calls == 1

    async def test_cached_entry_expires_with_the_ttl(self) -> None:
        record, plaintext = make_record()
        redis = FakeAsyncRedis()

        await authenticate(authenticator(FakeLoader(record), redis), plaintext)

        ttl = await redis.ttl(CACHE_PREFIX + record.public_id)
        assert 0 < ttl <= api_key_auth.RECORD_CACHE_SECONDS

    async def test_redis_down_falls_back_to_the_database(self) -> None:
        record, plaintext = make_record()
        server = FakeServer()
        server.connected = False
        loader = FakeLoader(record)

        await authenticate(
            authenticator(loader, FakeAsyncRedis(server=server)), plaintext
        )

        assert loader.calls == 1


def test_record_survives_a_json_round_trip() -> None:
    record, _ = make_record(allowed_origins=["https://site.com"])

    assert ApiKeyRecord.from_json(record.to_json()) == record


class TestInvalidateCache:
    def test_deletes_the_cached_records(self, monkeypatch: pytest.MonkeyPatch) -> None:
        redis = FakeRedis()
        redis.set(CACHE_PREFIX + "aaaa", "x")
        redis.set(CACHE_PREFIX + "bbbb", "x")
        monkeypatch.setattr(
            "server.services.security.api_key_auth.CONFIG.testing", False
        )
        monkeypatch.setattr(
            "server.services.security.api_key_auth.get_sync_redis", lambda: redis
        )

        invalidate_api_key_cache(["aaaa", "bbbb"])

        assert redis.keys("*") == []

    def test_is_a_no_op_in_tests(self, monkeypatch: pytest.MonkeyPatch) -> None:
        get_sync_redis = MagicMock()
        monkeypatch.setattr(
            "server.services.security.api_key_auth.get_sync_redis", get_sync_redis
        )

        invalidate_api_key_cache(["aaaa"])

        get_sync_redis.assert_not_called()

    def test_redis_errors_are_logged_not_raised(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        server = FakeServer()
        server.connected = False
        log = MagicMock()
        monkeypatch.setattr(
            "server.services.security.api_key_auth.CONFIG.testing", False
        )
        monkeypatch.setattr(
            "server.services.security.api_key_auth.get_sync_redis",
            lambda: FakeRedis(server=server),
        )
        monkeypatch.setattr("server.services.security.api_key_auth.logger", log)

        invalidate_api_key_cache(["aaaa"])

        assert "Failed to invalidate" in log.error.call_args.args[0]


@pytest.mark.asyncio
async def test_last_used_is_written_at_most_once_per_window() -> None:
    redis = FakeAsyncRedis()

    assert await should_write_last_used(redis, 7)
    assert not await should_write_last_used(redis, 7)
    assert await should_write_last_used(redis, 8)
    assert not await should_write_last_used(None, 7)


@pytest.mark.asyncio
async def test_last_used_is_skipped_when_redis_is_down() -> None:
    server = FakeServer()
    server.connected = False

    assert not await should_write_last_used(FakeAsyncRedis(server=server), 7)


def test_rejection_messages_are_generic() -> None:
    assert ApiKeyRejection(401, "revoked", "x").detail == INVALID_KEY_DETAIL
    assert ApiKeyRejection(401, "hash mismatch", "x").detail == INVALID_KEY_DETAIL
    assert ApiKeyRejection(403, "out of scope", "x").detail == FORBIDDEN_DETAIL
    assert "indisponíveis" in ApiKeyRejection(503, "no secret", "x").detail


class TestStartupCheck:
    def test_ready_with_a_secret(self) -> None:
        assert check_api_key_setup().startswith("API keys: ready")

    def test_error_without_a_secret(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "server.services.security.api_key_auth.CONFIG.api_key_secret", "short"
        )
        log = MagicMock()
        monkeypatch.setattr("server.services.security.api_key_auth.logger", log)

        message = check_api_key_setup()

        assert "missing or shorter" in message
        log.error.assert_called_once_with(message)
