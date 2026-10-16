"""Fixed-window rate limiting backed by Redis (see docs/RATE_LIMIT.md)."""

import ipaddress
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from redis.asyncio import Redis
from redis.exceptions import RedisError


class RateLimitMode(StrEnum):
    OFF = "off"
    # Counts and logs requests that would be blocked, but lets them through.
    SHADOW = "shadow"
    ENFORCE = "enforce"


@dataclass(frozen=True)
class RateLimitRule:
    max_requests: int
    window_seconds: int

    def __str__(self) -> str:
        return f"{self.max_requests}/{self.window_seconds}"


# Request-state key under which RateLimitMiddleware leaves a RateLimitEvent
# for LoggerMiddleware, which persists it to `apiaccesslog`.
RATE_LIMIT_EVENT_STATE_KEY = "rate_limit_event"


@dataclass(frozen=True)
class RateLimitEvent:
    """The first request over a limit in a window, for one client IP."""

    rule: RateLimitRule
    mode: RateLimitMode


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    # Values for the X-RateLimit-* headers, taken from the most restrictive
    # rule (the exceeded one when blocked).
    limit: int
    remaining: int
    reset_seconds: int
    exceeded: RateLimitRule | None = None
    # True only for the first request over the limit in a window, so a
    # flood logs one line per window instead of one per request.
    first_exceed: bool = False


def parse_rate_limits(spec: str) -> list[RateLimitRule]:
    """Parse "max/window_seconds" rules separated by commas, e.g.
    "40/10,150/60,5000/86400", sorted by window."""
    rules: list[RateLimitRule] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            max_requests, window_seconds = part.split("/")
            rule = RateLimitRule(int(max_requests), int(window_seconds))
        except ValueError as e:
            raise ValueError(
                f"Invalid rate limit rule {part!r}, expected 'max/window_seconds'"
            ) from e
        if rule.max_requests <= 0 or rule.window_seconds <= 0:
            raise ValueError(f"Rate limit rule {part!r} must be positive")
        rules.append(rule)
    windows = [rule.window_seconds for rule in rules]
    if len(set(windows)) != len(windows):
        raise ValueError(f"Duplicate window in rate limit rules {spec!r}")
    return sorted(rules, key=lambda rule: rule.window_seconds)


def resolve_rate_limit_config(
    mode: str, rules: str, *, testing: bool
) -> tuple[RateLimitMode, list[RateLimitRule]]:
    """Mode and rules from raw config values. The test suite always runs
    with rate limiting off, so a developer's .env can't turn API tests into
    429s. Raises ValueError on invalid values."""
    if testing:
        return RateLimitMode.OFF, []
    return RateLimitMode(mode.strip().lower()), parse_rate_limits(rules)


def client_identity(host: str) -> str:
    """Rate-limit key for a client address. IPv6 is collapsed to its /64,
    since a single subscriber usually controls a whole /64 and could
    otherwise rotate addresses to dodge the limit."""
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return host
    if isinstance(ip, ipaddress.IPv6Address):
        if ip.ipv4_mapped is not None:
            return str(ip.ipv4_mapped)
        return str(ipaddress.ip_network(f"{ip}/64", strict=False))
    return str(ip)


class FixedWindowRateLimiter:
    def __init__(
        self,
        redis: Redis,
        *,
        prefix: str = "rl",
        clock: Callable[[], float] = time.time,
    ) -> None:
        self.redis = redis
        self.prefix = prefix
        # Injectable so tests don't flake when requests straddle a window edge.
        self.clock = clock

    async def hit(
        self,
        identity: str,
        rules: list[RateLimitRule],
        now: float | None = None,
    ) -> RateLimitResult | None:
        """Count one request for `identity` against every rule. Returns None
        when Redis is unavailable, so callers can fail open."""
        now_s = int(self.clock() if now is None else now)
        pipe = self.redis.pipeline(transaction=False)
        for rule in rules:
            key = self.__key(identity, rule, now_s)
            pipe.incr(key)
            pipe.expire(key, rule.window_seconds)
        try:
            replies = await pipe.execute()
        except (RedisError, OSError):
            return None
        counts: list[int] = [int(count) for count in replies[0::2]]
        return self.__result(rules, counts, now_s)

    def __key(self, identity: str, rule: RateLimitRule, now_s: int) -> str:
        window_index = now_s // rule.window_seconds
        return f"{self.prefix}:{identity}:{rule.window_seconds}:{window_index}"

    @staticmethod
    def __result(
        rules: list[RateLimitRule], counts: list[int], now_s: int
    ) -> RateLimitResult:
        def reset(rule: RateLimitRule) -> int:
            return rule.window_seconds - now_s % rule.window_seconds

        exceeded = [
            (rule, count)
            for rule, count in zip(rules, counts)
            if count > rule.max_requests
        ]
        if exceeded:
            # Retry-After must cover the exceeded window that clears last.
            rule, count = max(exceeded, key=lambda item: reset(item[0]))
            return RateLimitResult(
                allowed=False,
                limit=rule.max_requests,
                remaining=0,
                reset_seconds=reset(rule),
                exceeded=rule,
                first_exceed=count == rule.max_requests + 1,
            )
        rule, count = min(
            zip(rules, counts), key=lambda item: item[0].max_requests - item[1]
        )
        return RateLimitResult(
            allowed=True,
            limit=rule.max_requests,
            remaining=rule.max_requests - count,
            reset_seconds=reset(rule),
        )
