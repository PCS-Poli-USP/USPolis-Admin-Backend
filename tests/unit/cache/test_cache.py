from datetime import date, timedelta
from typing import Any
from unittest.mock import patch

import pytest

import server.cache as cache_module
from server.cache import (
    clear_cache,
    clear_expired_cache,
    date_range_cache,
    get_cache_stats,
    simple_cache,
)
from server.deps.interval_dep import QueryInterval
from server.utils.brazil_datetime import BrazilDatetime


@pytest.fixture(autouse=True)
def _reset_cache_state() -> None:
    cache_module._cache_store.clear()
    cache_module._expired_map.clear()


class TestSimpleCacheSync:
    def test_second_call_is_served_from_cache(self) -> None:
        calls: list[int] = []

        @simple_cache(expire_seconds=60)
        def compute(x: int) -> int:
            calls.append(x)
            return x * 2

        assert compute(3) == 6
        assert compute(3) == 6
        assert calls == [3]

    def test_recomputes_after_expiry(self) -> None:
        calls: list[int] = []

        @simple_cache(expire_seconds=10)
        def compute() -> int:
            calls.append(1)
            return len(calls)

        base_time = BrazilDatetime.now_utc()
        with patch("server.cache.BrazilDatetime.now_utc", return_value=base_time):
            assert compute() == 1

        later = base_time + timedelta(seconds=20)
        with patch("server.cache.BrazilDatetime.now_utc", return_value=later):
            assert compute() == 2

        assert calls == [1, 1]


class TestSimpleCacheAsync:
    @pytest.mark.asyncio
    async def test_second_call_is_served_from_cache(self) -> None:
        calls: list[int] = []

        @simple_cache(expire_seconds=60)
        async def compute(x: int) -> int:
            calls.append(x)
            return x * 2

        assert await compute(5) == 10
        assert await compute(5) == 10
        assert calls == [5]


class TestClearCache:
    def test_clears_all_entries_and_returns_count(self) -> None:
        @simple_cache(expire_seconds=60)
        def a() -> int:
            return 1

        @simple_cache(expire_seconds=60)
        def b() -> int:
            return 2

        a()
        b()

        assert clear_cache() == 2
        assert clear_cache() == 0


class TestClearExpiredCache:
    def test_removes_only_expired_entries(self) -> None:
        @simple_cache(expire_seconds=10)
        def short_lived() -> int:
            return 1

        @simple_cache(expire_seconds=1000)
        def long_lived() -> int:
            return 2

        base_time = BrazilDatetime.now_utc()
        with patch("server.cache.BrazilDatetime.now_utc", return_value=base_time):
            short_lived()
            long_lived()

        later = base_time + timedelta(seconds=20)
        with patch("server.cache.BrazilDatetime.now_utc", return_value=later):
            removed = clear_expired_cache()

        assert removed == 1
        assert "cache:long_lived" in cache_module._cache_store
        assert "cache:short_lived" not in cache_module._cache_store


class TestGetCacheStats:
    def test_reports_key_age_and_expiration_status(self) -> None:
        @simple_cache(expire_seconds=10)
        def short_lived() -> int:
            return 1

        base_time = BrazilDatetime.now_utc()
        with patch("server.cache.BrazilDatetime.now_utc", return_value=base_time):
            short_lived()

        later = base_time + timedelta(seconds=20)
        with patch("server.cache.BrazilDatetime.now_utc", return_value=later):
            stats = get_cache_stats()

        assert stats.total_keys == 1
        entry = stats.keys[0]
        assert entry.key == "cache:short_lived"
        assert entry.age_seconds == 20
        assert entry.expired is True


class TestDateRangeCacheSync:
    def test_caches_when_dates_are_within_current_window(self) -> None:
        calls: list[Any] = []

        @date_range_cache(expire_seconds=60)
        def report(*, start: date, end: date) -> int:
            calls.append((start, end))
            return len(calls)

        today = BrazilDatetime.now_utc().date()
        assert report(start=today, end=today) == 1
        assert report(start=today, end=today) == 1
        assert len(calls) == 1

    def test_bypasses_cache_when_dates_are_outside_window(self) -> None:
        calls: list[Any] = []

        @date_range_cache(expire_seconds=60)
        def report(*, start: date, end: date) -> int:
            calls.append((start, end))
            return len(calls)

        far_future = BrazilDatetime.now_utc().date() + timedelta(days=365)
        assert report(start=far_future, end=far_future) == 1
        assert report(start=far_future, end=far_future) == 2
        assert len(calls) == 2

    def test_uses_interval_param_when_configured(self) -> None:
        """report() must accept **kwargs (not just `interval`), since the
        decorator's interval_param branch still unconditionally injects
        start/end kwargs into the call - see the note on date_range_cache
        about that being a latent bug for any real interval_param caller."""
        calls: list[Any] = []

        @date_range_cache(expire_seconds=60, interval_param="interval")
        def report(*, interval: QueryInterval, **kwargs: Any) -> int:
            calls.append(interval)
            return len(calls)

        today = BrazilDatetime.now_utc().date()
        interval = QueryInterval(start=today, end=today)
        assert report(interval=interval) == 1
        assert report(interval=interval) == 1
        assert len(calls) == 1


class TestDateRangeCacheAsync:
    @pytest.mark.asyncio
    async def test_caches_when_dates_are_within_current_window(self) -> None:
        calls: list[Any] = []

        @date_range_cache(expire_seconds=60)
        async def report(*, start: date, end: date) -> int:
            calls.append((start, end))
            return len(calls)

        today = BrazilDatetime.now_utc().date()
        assert await report(start=today, end=today) == 1
        assert await report(start=today, end=today) == 1
        assert len(calls) == 1

    @pytest.mark.asyncio
    async def test_bypasses_cache_when_dates_are_outside_window(self) -> None:
        calls: list[Any] = []

        @date_range_cache(expire_seconds=60)
        async def report(*, start: date, end: date) -> int:
            calls.append((start, end))
            return len(calls)

        far_future = BrazilDatetime.now_utc().date() + timedelta(days=365)
        assert await report(start=far_future, end=far_future) == 1
        assert await report(start=far_future, end=far_future) == 2
        assert len(calls) == 2
