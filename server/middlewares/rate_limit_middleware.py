import time
from fastapi.responses import JSONResponse
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from server.config import CONFIG
from server.logger import logger
from server.middlewares.request_utils import app_path
from server.services.rate_limiter import (
    RATE_LIMIT_EVENT_STATE_KEY,
    FixedWindowRateLimiter,
    RateLimitEvent,
    RateLimitMode,
    RateLimitResult,
    RateLimitRule,
    client_identity,
    resolve_rate_limit_config,
)
from server.services.redis_client import get_redis
from server.services.security.api_key_auth import (
    API_KEY_IDENTITY_STATE_KEY,
    ApiKeyIdentity,
)


# Paths (relative to the /api root path) never counted by the rate limiter:
# health checks are API-key protected and polled by monitoring.
RATE_LIMIT_EXEMPT_PATHS = ("/health", "/docs", "/redoc", "/openapi.json")
REDIS_ERROR_LOG_INTERVAL_SECONDS = 60


def rate_limit_headers(result: RateLimitResult) -> dict[str, str]:
    return {
        "X-RateLimit-Limit": str(result.limit),
        "X-RateLimit-Remaining": str(result.remaining),
        "X-RateLimit-Reset": str(result.reset_seconds),
    }


class RateLimitMiddleware:
    """Per-IP fixed-window rate limit on every request (see docs/RATE_LIMIT.md).

    Pure ASGI and placed before routing and authentication, so a rejected
    request costs one Redis round trip and nothing else - in particular, no
    Google token validation. Fails open when Redis is unavailable.
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        mode: RateLimitMode | None = None,
        rules: list[RateLimitRule] | None = None,
        limiter: FixedWindowRateLimiter | None = None,
    ) -> None:
        self.app = app
        # Explicit mode/rules (tests) skip the config; otherwise read it.
        # Redis reachability is reported once at startup by
        # `check_rate_limit_setup` (see the app lifespan).
        config_mode: RateLimitMode = RateLimitMode.OFF
        config_rules: list[RateLimitRule] = []
        if mode is None or rules is None:
            try:
                config_mode, config_rules = resolve_rate_limit_config(
                    CONFIG.rate_limit_mode,
                    CONFIG.anon_rate_limits,
                    testing=CONFIG.testing,
                )
            except ValueError as e:
                # Starlette builds middlewares on the first request, so
                # raising here would turn every request into a 500.
                # Fail open: config_mode/config_rules stay off/empty.
                logger.error(f"Invalid rate limit config, rate limiting disabled: {e}")

        self.mode = mode if mode is not None else config_mode
        self.rules = rules if rules is not None else config_rules
        self.limiter = limiter
        self.last_redis_error_log = 0.0

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if not self.__applies_to(scope):
            await self.app(scope, receive, send)
            return
        limiter = self.__get_limiter()
        client = scope.get("client")
        if limiter is None or client is None:
            await self.app(scope, receive, send)
            return

        result = await self.__hit(limiter, scope, client[0])
        if result is None:
            self.__log_redis_failure()
            await self.app(scope, receive, send)
            return

        if not result.allowed and result.first_exceed and result.exceeded:
            logger.warning(
                f'type="RateLimit" mode="{self.mode}" host="{client[0]}" '
                f'method="{scope["method"]}" path="{app_path(scope)}" '
                f'rule="{result.exceeded}"'
            )
            # Picked up by LoggerMiddleware, which persists only this first
            # hit per IP and window (see __persist_rate_limit_event).
            scope.setdefault("state", {})[RATE_LIMIT_EVENT_STATE_KEY] = RateLimitEvent(
                rule=result.exceeded, mode=self.mode
            )

        if self.mode == RateLimitMode.SHADOW:
            await self.app(scope, receive, send)
            return

        headers = rate_limit_headers(result)
        if not result.allowed:
            response = JSONResponse(
                {
                    "detail": "Muitas requisições. Tente novamente em "
                    f"{result.reset_seconds} segundos."
                },
                status_code=429,
                headers={**headers, "Retry-After": str(result.reset_seconds)},
            )
            await response(scope, receive, send)
            return

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message).update(headers)
            await send(message)

        await self.app(scope, receive, send_with_headers)

    async def __hit(
        self, limiter: FixedWindowRateLimiter, scope: Scope, host: str
    ) -> RateLimitResult | None:
        """Requests with a valid API key count against the key's limits
        instead of the anonymous per-IP ones. Browser keys are public, so
        their visitors also keep the per-IP limit: one client reusing a
        visible key can't burn the partner's whole quota."""
        ip_bucket = f"ip:{client_identity(host)}"
        identity: ApiKeyIdentity | None = (scope.get("state") or {}).get(
            API_KEY_IDENTITY_STATE_KEY
        )
        if identity is None:
            return await limiter.hit(ip_bucket, self.rules)
        key_result = await limiter.hit(f"key:{identity.key_id}", identity.rules)
        if not identity.is_browser_key or key_result is None:
            return key_result
        if not key_result.allowed:
            return key_result
        ip_result = await limiter.hit(ip_bucket, self.rules)
        if ip_result is not None and not ip_result.allowed:
            return ip_result
        return key_result

    def __applies_to(self, scope: Scope) -> bool:
        return (
            scope["type"] == "http"
            and self.mode != RateLimitMode.OFF
            and bool(self.rules)
            and scope["method"] != "OPTIONS"
            and not app_path(scope).startswith(RATE_LIMIT_EXEMPT_PATHS)
        )

    def __get_limiter(self) -> FixedWindowRateLimiter | None:
        if self.limiter is None:
            redis = get_redis()
            if redis is not None:
                self.limiter = FixedWindowRateLimiter(redis)
        return self.limiter

    def __log_redis_failure(self) -> None:
        now = time.monotonic()
        if now - self.last_redis_error_log >= REDIS_ERROR_LOG_INTERVAL_SECONDS:
            self.last_redis_error_log = now
            logger.error("Rate limit: Redis unavailable, letting requests through")
