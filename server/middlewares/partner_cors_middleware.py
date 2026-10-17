"""CORS for partner sites (see docs/API_KEYS.md, "Browser keys").

Starlette's CORSMiddleware serves first-party origins (ALLOWED_ORIGINS), with
credentials. It rejects every other origin's preflight with 400, so this
middleware runs outside it and handles partner origins: the origins of
usable browser keys. Partners get GET/HEAD on public routes, and **never**
credentials, so a partner page can't make requests with our users' session
cookie.

CORS is not the security gate: ApiKeyMiddleware checks each request's Origin
against its own key. This layer only lets the browser read the response.
"""

import time
from collections.abc import Callable
from typing import Any

from anyio import to_thread
from starlette.datastructures import Headers, MutableHeaders
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from server.config import CONFIG
from server.db import get_db
from server.logger import logger
from server.middlewares.api_key_middleware import matched_route_is_public
from server.services.security.api_key_auth import db_partner_origins_loader

PARTNER_METHODS = ("GET", "HEAD")
PARTNER_ALLOWED_HEADERS = "Accept, Accept-Language, Content-Language, X-API-Key"
PARTNER_EXPOSED_HEADERS = (
    "Retry-After, X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset"
)
PREFLIGHT_MAX_AGE_SECONDS = 600
# Per worker, so random Origin headers can't trigger a DB query per request.
# A new or revoked browser key's origin is picked up within this delay.
ORIGINS_CACHE_SECONDS = 30


class PartnerCorsMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        origins_loader: Callable[[], set[str]] | None = None,
        cache_seconds: float | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.app = app
        # Injected in unit tests; otherwise built from the app's DB session.
        self.origins_loader = origins_loader
        self.cache_seconds = (
            cache_seconds
            if cache_seconds is not None
            else (0 if CONFIG.testing else ORIGINS_CACHE_SECONDS)
        )
        # Injectable: patching time.monotonic would also hit the event loop.
        self.clock = clock
        self.cached_origins: set[str] = set()
        self.cached_at = float("-inf")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = Headers(scope=scope)
        origin = headers.get("origin")
        if origin is None or origin in CONFIG.allowed_origins:
            # No CORS involved, or a first-party origin: CORSMiddleware's job.
            await self.app(scope, receive, send)
            return

        is_preflight = (
            scope["method"] == "OPTIONS" and "access-control-request-method" in headers
        )
        method = (
            headers["access-control-request-method"].upper()
            if is_preflight
            else scope["method"]
        )
        if (
            method not in PARTNER_METHODS
            or matched_route_is_public(scope) is not True
            or origin.lower() not in await self.__partner_origins(scope)
        ):
            # Not a partner request: the inner CORSMiddleware refuses it.
            await self.app(scope, receive, send)
            return

        if is_preflight:
            response = Response(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": origin,
                    "Access-Control-Allow-Methods": ", ".join(PARTNER_METHODS),
                    "Access-Control-Allow-Headers": PARTNER_ALLOWED_HEADERS,
                    "Access-Control-Max-Age": str(PREFLIGHT_MAX_AGE_SECONDS),
                    "Vary": "Origin",
                },
            )
            await response(scope, receive, send)
            return

        async def send_with_cors(message: Message) -> None:
            if message["type"] == "http.response.start":
                response_headers = MutableHeaders(scope=message)
                # The inner CORSMiddleware adds Allow-Credentials to every
                # response, even for origins it doesn't allow. Next to our
                # Allow-Origin it would let a partner page send our users'
                # session cookie, so it must go.
                if "access-control-allow-credentials" in response_headers:
                    del response_headers["access-control-allow-credentials"]
                response_headers["Access-Control-Allow-Origin"] = origin
                response_headers["Access-Control-Expose-Headers"] = (
                    PARTNER_EXPOSED_HEADERS
                )
                response_headers.add_vary_header("Origin")
            await send(message)

        await self.app(scope, receive, send_with_cors)

    async def __partner_origins(self, scope: Scope) -> set[str]:
        now = self.clock()
        if now - self.cached_at < self.cache_seconds:
            return self.cached_origins
        loader = self.origins_loader or db_partner_origins_loader(
            self.__session_provider(scope)
        )
        try:
            origins = await to_thread.run_sync(loader)
        except Exception as e:  # fail closed for CORS: no partner origins
            logger.error(f"Failed to load partner CORS origins: {e}")
            return set()
        self.cached_origins, self.cached_at = origins, now
        return origins

    @staticmethod
    def __session_provider(scope: Scope) -> Callable[[], Any]:
        # Honors dependency_overrides, so tests use their own session.
        app = scope.get("app")
        overrides = getattr(app, "dependency_overrides", {})
        return overrides.get(get_db, get_db)  # type: ignore[no-any-return]
