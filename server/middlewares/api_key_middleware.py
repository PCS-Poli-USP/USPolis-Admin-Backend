import time
from urllib.parse import parse_qs
from typing import Any
from collections.abc import Callable
from fastapi import status
from fastapi.responses import JSONResponse
from anyio import to_thread
from redis.asyncio import Redis
from redis.exceptions import RedisError
from starlette.datastructures import Headers
from starlette.routing import Match
from starlette.types import ASGIApp, Receive, Scope, Send

from server.config import CONFIG
from server.db import get_db
from server.logger import logger
from server.middlewares.request_utils import app_path
from server.services.rate_limiter import (
    client_identity,
)
from server.services.redis_client import get_redis
from server.services.security.api_key_auth import (
    API_KEY_HEADER,
    API_KEY_IDENTITY_STATE_KEY,
    ApiKeyAuthenticator,
    ApiKeyRejection,
    db_last_used_writer,
    db_record_loader,
    should_write_last_used,
)


# A key in the URL ends up in logs, proxies and browser history.
API_KEY_QUERY_PARAMS = frozenset({"api_key", "apikey", "x-api-key", "x_api_key"})
# Failed key attempts per IP before answering 429 without even looking the
# key up, so guessing keys can't flood the database or the logs.
AUTH_FAILURE_LIMIT = 20
AUTH_FAILURE_WINDOW_SECONDS = 60
AUTH_FAILURE_PREFIX = "apikey:fail:"


def matched_route_is_public(scope: Scope) -> bool | None:
    """Whether the route this request will hit is public-tier (tagged
    "Public" by the public router). None when no route matches. Needed
    because the middleware runs before routing, and authenticated routes
    have no URL prefix to tell them apart."""
    app = scope.get("app")
    router = getattr(app, "router", None)
    partial: bool | None = None
    for route in getattr(router, "routes", []):
        match, _ = route.matches(scope)
        tags = getattr(route, "tags", None) or []
        if match == Match.FULL:
            return "Public" in tags
        if match == Match.PARTIAL and partial is None:
            partial = "Public" in tags
    return partial


class ApiKeyMiddleware:
    """Authenticates requests that carry `X-API-Key` (see docs/API_KEYS.md).

    Without the header, requests pass through as anonymous. With it, the
    key must be valid and allowed for this request, or the request is
    rejected (401/403) with a generic message; the real reason is only
    logged. A valid key's identity is left on the request state for
    RateLimitMiddleware (its own limits) and LoggerMiddleware (`api_key_id`).
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        authenticator: ApiKeyAuthenticator | None = None,
        redis: Redis | None = None,
        last_used_writer: Callable[[int], None] | None = None,
    ) -> None:
        self.app = app
        # Injected in tests; otherwise built per request (see below).
        self.authenticator = authenticator
        self.injected_redis = redis
        self.last_used_writer = last_used_writer

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["method"] == "OPTIONS":
            await self.app(scope, receive, send)
            return
        if self.__key_in_query(scope):
            response = JSONResponse(
                {"detail": "Envie a API key no header X-API-Key, nunca na URL."},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            await response(scope, receive, send)
            return
        headers = Headers(scope=scope)
        plaintext = headers.get(API_KEY_HEADER)
        if plaintext is None:
            await self.app(scope, receive, send)
            return

        host = scope["client"][0] if scope.get("client") else "unknown"
        redis = self.__redis()
        if await self.__too_many_failures(redis, host):
            response = JSONResponse(
                {"detail": "Muitas tentativas com API key inválida. Aguarde."},
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={"Retry-After": str(AUTH_FAILURE_WINDOW_SECONDS)},
            )
            await response(scope, receive, send)
            return

        provider = self.__session_provider(scope)
        authenticator = self.authenticator or ApiKeyAuthenticator(
            db_record_loader(provider), redis
        )
        path = app_path(scope)
        try:
            identity = await authenticator.authenticate(
                plaintext.strip(),
                method=scope["method"],
                path=path,
                origin=headers.get("origin"),
                is_public_route=matched_route_is_public(scope),
            )
        except ApiKeyRejection as rejection:
            logger.warning(
                f'type="ApiKeyRejected" status="{rejection.status_code}" '
                f'host="{host}" method="{scope["method"]}" path="{path}" '
                f'public_id="{rejection.public_id or "N/A"}" '
                f'reason="{rejection.reason}"'
            )
            await self.__count_failure(redis, host)
            response = JSONResponse(
                {"detail": rejection.detail},
                status_code=rejection.status_code,
                headers=(
                    {"WWW-Authenticate": "ApiKey"}
                    if rejection.status_code == 401
                    else None
                ),
            )
            await response(scope, receive, send)
            return

        scope.setdefault("state", {})[API_KEY_IDENTITY_STATE_KEY] = identity
        await self.__touch_last_used(redis, provider, identity.key_id)
        await self.app(scope, receive, send)

    def __redis(self) -> Redis | None:
        if self.injected_redis is not None:
            return self.injected_redis
        return None if CONFIG.testing else get_redis()

    @staticmethod
    def __session_provider(scope: Scope) -> Callable[[], Any]:
        # Honors dependency_overrides, so tests use their own session.
        app = scope.get("app")
        overrides = getattr(app, "dependency_overrides", {})
        return overrides.get(get_db, get_db)  # type: ignore[no-any-return]

    @staticmethod
    def __key_in_query(scope: Scope) -> bool:
        query = scope.get("query_string", b"").decode("latin-1")
        return any(
            name.lower() in API_KEY_QUERY_PARAMS
            for name in parse_qs(query, keep_blank_values=True)
        )

    async def __touch_last_used(
        self, redis: Redis | None, provider: Callable[[], Any], key_id: int
    ) -> None:
        if not await should_write_last_used(redis, key_id):
            return
        writer = self.last_used_writer or db_last_used_writer(provider)
        try:
            await to_thread.run_sync(writer, key_id)
        except Exception as e:  # never fail the request over a metric
            logger.error(f"Failed to update API key last_used_at: {e}")

    @staticmethod
    def __failure_bucket(host: str) -> str:
        window = int(time.time()) // AUTH_FAILURE_WINDOW_SECONDS
        return f"{AUTH_FAILURE_PREFIX}{client_identity(host)}:{window}"

    async def __too_many_failures(self, redis: Redis | None, host: str) -> bool:
        if redis is None:
            return False
        try:
            count = await redis.get(self.__failure_bucket(host))
        except (RedisError, OSError):
            return False
        return count is not None and int(count) >= AUTH_FAILURE_LIMIT

    async def __count_failure(self, redis: Redis | None, host: str) -> None:
        if redis is None:
            return
        bucket = self.__failure_bucket(host)
        try:
            pipe = redis.pipeline(transaction=False)
            pipe.incr(bucket)
            pipe.expire(bucket, AUTH_FAILURE_WINDOW_SECONDS)
            await pipe.execute()
        except (RedisError, OSError):
            pass
