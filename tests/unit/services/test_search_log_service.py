from collections.abc import Iterator
from datetime import date

import pytest
from fakeredis import FakeAsyncRedis, FakeServer
from redis.exceptions import ConnectionError as RedisConnectionError

from server.services import search_log_service
from server.services.search_log_service import (
    IP_QUOTA_KEY_TTL_SECONDS,
    ip_quota_key,
    take_new_query_slot,
)

DAY = date(2026, 11, 22)


@pytest.fixture(name="redis")
def redis_fixture(monkeypatch: pytest.MonkeyPatch) -> Iterator[FakeAsyncRedis]:
    redis = FakeAsyncRedis(server=FakeServer())
    monkeypatch.setattr(search_log_service, "get_redis", lambda: redis)
    monkeypatch.setattr(
        search_log_service.CONFIG, "search_log_max_new_queries_per_ip_per_day", 2
    )
    yield redis


def test_quota_key_groups_ipv6_by_64_and_names_the_day() -> None:
    assert ip_quota_key("203.0.113.7", DAY) == "sl:ip:203.0.113.7:2026-11-22"
    assert ip_quota_key("2001:db8::1", DAY) == ip_quota_key("2001:db8::ffff", DAY)
    assert ip_quota_key(None, DAY) == "sl:ip:unknown:2026-11-22"


@pytest.mark.asyncio
async def test_allows_up_to_the_quota_then_refuses(redis: FakeAsyncRedis) -> None:
    results = [await take_new_query_slot("203.0.113.7", DAY) for _ in range(3)]

    assert results == [True, True, False]
    assert (
        0
        < await redis.ttl(ip_quota_key("203.0.113.7", DAY))
        <= (IP_QUOTA_KEY_TTL_SECONDS)
    )


@pytest.mark.asyncio
async def test_ips_and_days_are_counted_separately(redis: FakeAsyncRedis) -> None:
    for _ in range(2):
        await take_new_query_slot("203.0.113.7", DAY)

    assert await take_new_query_slot("198.51.100.9", DAY)
    assert await take_new_query_slot("203.0.113.7", date(2026, 11, 23))
    assert not await take_new_query_slot("203.0.113.7", DAY)


@pytest.mark.asyncio
async def test_fails_open_without_redis(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(search_log_service, "get_redis", lambda: None)

    assert await take_new_query_slot("203.0.113.7", DAY)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error", [RedisConnectionError("down"), RuntimeError("other event loop")]
)
async def test_fails_open_when_redis_errors(
    redis: FakeAsyncRedis, monkeypatch: pytest.MonkeyPatch, error: Exception
) -> None:
    def broken_pipeline(*args: object, **kwargs: object) -> None:
        raise error

    monkeypatch.setattr(redis, "pipeline", broken_pipeline)

    assert await take_new_query_slot("203.0.113.7", DAY)
