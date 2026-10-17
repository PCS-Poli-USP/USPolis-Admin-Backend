from urllib.parse import urlsplit, urlunsplit

from redis import Redis as SyncRedis
from redis.asyncio import Redis
from redis.exceptions import RedisError

from server.config import CONFIG
from server.logger import logger
from server.services.rate_limiter import RateLimitMode, resolve_rate_limit_config

# Short timeouts on purpose: Redis sits on the request hot path (rate
# limiting), and a slow or dead Redis must fail open fast instead of
# holding requests.
REDIS_SOCKET_TIMEOUT_SECONDS = 0.2

_redis: Redis | None = None
_sync_redis: SyncRedis | None = None


def get_redis() -> Redis | None:
    """Lazily build one async client per worker process. Returns None when
    `REDIS_URL` is not configured."""
    global _redis
    if not CONFIG.redis_url:
        return None
    if _redis is None:
        _redis = Redis.from_url(
            CONFIG.redis_url,
            socket_timeout=REDIS_SOCKET_TIMEOUT_SECONDS,
            socket_connect_timeout=REDIS_SOCKET_TIMEOUT_SECONDS,
            health_check_interval=30,
        )
    return _redis


def get_sync_redis() -> SyncRedis | None:
    """Blocking client for sync code paths (e.g. admin routes invalidating
    cached API keys). Same timeouts; None without `REDIS_URL`."""
    global _sync_redis
    if not CONFIG.redis_url:
        return None
    if _sync_redis is None:
        _sync_redis = SyncRedis.from_url(
            CONFIG.redis_url,
            socket_timeout=REDIS_SOCKET_TIMEOUT_SECONDS,
            socket_connect_timeout=REDIS_SOCKET_TIMEOUT_SECONDS,
        )
    return _sync_redis


def redact_url(url: str) -> str:
    """`url` with its password masked, safe for logs."""
    parts = urlsplit(url)
    if parts.password is None:
        return url
    host = parts.netloc.rsplit("@", 1)[1]
    return urlunsplit(parts._replace(netloc=f"{parts.username or ''}:***@{host}"))


async def check_rate_limit_setup() -> str:
    """Startup check: is rate limiting on, and can it reach Redis? Logs the
    outcome (error level when misconfigured) and returns the same message,
    which the lifespan also prints: app_logger only reaches the console
    with DEBUG=True."""
    try:
        mode, rules = resolve_rate_limit_config(
            CONFIG.rate_limit_mode, CONFIG.anon_rate_limits, testing=CONFIG.testing
        )
    except ValueError as e:
        message = f"Rate limit: invalid config, rate limiting disabled ({e})"
        logger.error(message)
        return message

    if mode == RateLimitMode.OFF:
        reason = "testing" if CONFIG.testing else "RATE_LIMIT_MODE=off"
        message = f"Rate limit: disabled ({reason})"
        logger.info(message)
        return message

    redis = get_redis()
    if redis is None:
        message = (
            f"Rate limit: RATE_LIMIT_MODE={mode} but REDIS_URL is empty, "
            "rate limiting disabled (fail-open)"
        )
        logger.error(message)
        return message

    target = redact_url(CONFIG.redis_url)
    try:
        await redis.ping()
    except (RedisError, OSError) as e:
        message = (
            f"Rate limit: Redis unreachable at {target} ({e}); requests pass "
            "unlimited until it is back (fail-open)"
        )
        logger.error(message)
        return message

    rules_str = ", ".join(str(rule) for rule in rules)
    message = f"Rate limit: Redis OK at {target}, mode={mode}, rules={rules_str}"
    logger.info(message)
    return message
