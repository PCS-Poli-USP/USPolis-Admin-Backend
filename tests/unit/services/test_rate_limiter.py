import pytest
from fakeredis import FakeAsyncRedis, FakeServer

from server.services.rate_limiter import (
    FixedWindowRateLimiter,
    RateLimitMode,
    RateLimitRule,
    client_identity,
    parse_rate_limits,
    resolve_rate_limit_config,
)

# Aligned to every window used below (10, 60 and 86400 all divide it), so
# `NOW` is the first second of each window.
NOW = 1_800_000_000 - 1_800_000_000 % 86400


class TestParseRateLimits:
    def test_parses_and_sorts_by_window(self) -> None:
        assert parse_rate_limits("5000/86400, 40/10,150/60") == [
            RateLimitRule(40, 10),
            RateLimitRule(150, 60),
            RateLimitRule(5000, 86400),
        ]

    def test_empty_spec_means_no_rules(self) -> None:
        assert parse_rate_limits("") == []

    @pytest.mark.parametrize(
        "spec", ["40", "40/", "a/10", "40/10/2", "0/10", "40/0", "-1/10"]
    )
    def test_rejects_malformed_or_non_positive_rules(self, spec: str) -> None:
        with pytest.raises(ValueError):
            parse_rate_limits(spec)

    def test_rejects_duplicate_windows(self) -> None:
        with pytest.raises(ValueError, match="Duplicate window"):
            parse_rate_limits("10/60,20/60")

    def test_rule_str_round_trips(self) -> None:
        assert str(RateLimitRule(150, 60)) == "150/60"


class TestClientIdentity:
    def test_ipv4_is_kept(self) -> None:
        assert client_identity("143.107.10.20") == "143.107.10.20"

    def test_ipv6_is_collapsed_to_its_64(self) -> None:
        a = client_identity("2804:14c:1:2:aaaa::1")
        b = client_identity("2804:14c:1:2:bbbb::2")
        assert a == b == "2804:14c:1:2::/64"

    def test_ipv4_mapped_ipv6_becomes_ipv4(self) -> None:
        assert client_identity("::ffff:143.107.10.20") == "143.107.10.20"

    def test_non_ip_host_is_kept_as_is(self) -> None:
        assert client_identity("testclient") == "testclient"


@pytest.fixture
def redis() -> FakeAsyncRedis:
    return FakeAsyncRedis()


@pytest.fixture
def limiter(redis: FakeAsyncRedis) -> FixedWindowRateLimiter:
    return FixedWindowRateLimiter(redis)


@pytest.mark.asyncio
async def test_allows_up_to_the_limit_then_blocks(
    limiter: FixedWindowRateLimiter,
) -> None:
    rules = [RateLimitRule(3, 60)]
    results = [await limiter.hit("ip:1.1.1.1", rules, now=NOW) for _ in range(5)]

    assert [r.allowed for r in results if r] == [True, True, True, False, False]
    assert [r.remaining for r in results if r] == [2, 1, 0, 0, 0]


@pytest.mark.asyncio
async def test_first_exceed_is_flagged_once_per_window(
    limiter: FixedWindowRateLimiter,
) -> None:
    rules = [RateLimitRule(1, 60)]
    results = [await limiter.hit("ip:1.1.1.1", rules, now=NOW) for _ in range(4)]

    assert [r.first_exceed for r in results if r] == [False, True, False, False]


@pytest.mark.asyncio
async def test_counter_resets_in_the_next_window(
    limiter: FixedWindowRateLimiter,
) -> None:
    rules = [RateLimitRule(1, 60)]
    await limiter.hit("ip:1.1.1.1", rules, now=NOW)
    blocked = await limiter.hit("ip:1.1.1.1", rules, now=NOW + 59)
    next_window = await limiter.hit("ip:1.1.1.1", rules, now=NOW + 60)

    assert blocked is not None and not blocked.allowed
    assert blocked.reset_seconds == 1
    assert next_window is not None and next_window.allowed


@pytest.mark.asyncio
async def test_identities_are_counted_separately(
    limiter: FixedWindowRateLimiter,
) -> None:
    rules = [RateLimitRule(1, 60)]
    await limiter.hit("ip:1.1.1.1", rules, now=NOW)
    other = await limiter.hit("ip:2.2.2.2", rules, now=NOW)

    assert other is not None and other.allowed


@pytest.mark.asyncio
async def test_all_rules_are_enforced_together(
    limiter: FixedWindowRateLimiter,
) -> None:
    # The 10s burst rule allows 5, but the daily rule only allows 3.
    rules = [RateLimitRule(5, 10), RateLimitRule(3, 86400)]
    results = [await limiter.hit("ip:1.1.1.1", rules, now=NOW) for _ in range(4)]

    blocked = results[-1]
    assert blocked is not None and not blocked.allowed
    assert blocked.exceeded == RateLimitRule(3, 86400)
    assert blocked.limit == 3
    assert blocked.reset_seconds == 86400


@pytest.mark.asyncio
async def test_headers_follow_the_most_restrictive_rule(
    limiter: FixedWindowRateLimiter,
) -> None:
    rules = [RateLimitRule(2, 10), RateLimitRule(100, 60)]
    result = await limiter.hit("ip:1.1.1.1", rules, now=NOW + 3)

    assert result is not None
    assert (result.limit, result.remaining, result.reset_seconds) == (2, 1, 7)


@pytest.mark.asyncio
async def test_keys_expire_with_their_window(
    limiter: FixedWindowRateLimiter, redis: FakeAsyncRedis
) -> None:
    await limiter.hit("ip:1.1.1.1", [RateLimitRule(10, 60)], now=NOW)

    keys = await redis.keys("rl:ip:1.1.1.1:60:*")
    assert len(keys) == 1
    assert 0 < await redis.ttl(keys[0]) <= 60


@pytest.mark.asyncio
async def test_returns_none_when_redis_is_unavailable() -> None:
    server = FakeServer()
    server.connected = False
    limiter = FixedWindowRateLimiter(FakeAsyncRedis(server=server))

    assert await limiter.hit("ip:1.1.1.1", [RateLimitRule(1, 60)], now=NOW) is None


class TestResolveRateLimitConfig:
    def test_parses_mode_and_rules(self) -> None:
        mode, rules = resolve_rate_limit_config(" Enforce ", "40/10", testing=False)

        assert mode == RateLimitMode.ENFORCE
        assert rules == [RateLimitRule(40, 10)]

    def test_testing_forces_off_whatever_the_config(self) -> None:
        assert resolve_rate_limit_config("enforce", "1/60", testing=True) == (
            RateLimitMode.OFF,
            [],
        )

    @pytest.mark.parametrize(("mode", "rules"), [("block-all", "40/10"), ("off", "x")])
    def test_invalid_values_raise(self, mode: str, rules: str) -> None:
        with pytest.raises(ValueError):
            resolve_rate_limit_config(mode, rules, testing=False)
