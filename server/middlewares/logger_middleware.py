import json
import time
import traceback
from typing import Any
from collections.abc import Callable
from urllib.parse import unquote_plus
from fastapi import Request, Response, status
from pydantic import BaseModel
from sqlmodel import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from server.config import CONFIG
from server.db import engine
from server.logger import logger, loki_access_logger
from server.middlewares.request_utils import get_client_ip
from server.repositories.api_access_log_repository import ApiAccessLogRepository
from server.services.auth.auth_user_info import AuthUserInfo
from server.services.rate_limiter import (
    RATE_LIMIT_EVENT_STATE_KEY,
    RateLimitEvent,
    RateLimitMode,
)
from server.services.security.api_key_auth import (
    API_KEY_IDENTITY_STATE_KEY,
    ApiKeyIdentity,
)
from server.services.security.api_key_crypto import API_KEY_PATTERN
from server.utils.enums.api_security_level_enum import APISecurityLevel


class RoutesDescription(BaseModel):
    method: str
    start_with: str
    end_with: str


# Rules for which method+path combos get their body logged: on the
# "Request" log line always, and on the "Response" log line whenever that
# response is an error (status_code >= 400) — see `LoggerMiddleware`.
LOG_BODY_RULES = {
    "GET": {
        "start_with": ["/admin"],
        "end_with": [""],
    },
    "POST": {
        "start_with": ["/admin", "/subjects", "/classes", "/classrooms", "/calendars"],
        "end_with": [""],
    },
    "PUT": {
        "start_with": ["/classes", "/classrooms", "/admin"],
        "end_with": [""],
    },
    "PATCH": {
        "start_with": ["/classes", "/classrooms"],
        "end_with": [""],
    },
    "DELETE": {
        "start_with": ["/admin"],
        "end_with": [""],
    },
}

LOKI_EXCLUDED_PATHS = (
    "/health",
    "/analytics",
    "/api/docs",
    "/api/openapi.json",
)

# Keys redacted (case-insensitive) from any request body before it's logged
# or persisted - e.g. JupiterLoginRequest.password carries the user's real
# USP Jupiter password, and a wrong-password crawl attempt is exactly the
# case that trips the error-response body persistence below.
# `token` is the secret of a one-time API key delivery link (posted to
# /api-key-links/.../reveal and to the admin share-link email route).
# `code` is deliberately absent: it is a subject/course code in most bodies.
SENSITIVE_BODY_KEYS = frozenset(
    {
        "password",
        "token",
        "refresh_token",
        "access_token",
        "id_token",
        "auth_code",
        "client_secret",
        "secret",
        "api_key",
    }
)

# Query parameter names (case-insensitive) whose values are redacted from the
# logged URL. GET /auth/refresh-token takes the user's Google refresh token
# in the query string, and /auth/get-tokens takes the OAuth `auth_code`.
SENSITIVE_QUERY_KEYS = SENSITIVE_BODY_KEYS | frozenset(
    {"code", "key", "apikey", "x-api-key", "x_api_key"}
)

REDACTED = "***REDACTED***"


def redact_query(query: str) -> str:
    """Redact `SENSITIVE_QUERY_KEYS` values from a raw query string, keeping
    every other parameter byte-for-byte as it was received."""
    if not query:
        return query
    parts = []
    for part in query.split("&"):
        name, sep, _ = part.partition("=")
        if sep and unquote_plus(name).lower() in SENSITIVE_QUERY_KEYS:
            parts.append(f"{name}={REDACTED}")
        else:
            parts.append(part)
    return "&".join(parts)


def redact_sensitive_fields(data: Any) -> Any:
    """Recursively redact `SENSITIVE_BODY_KEYS` from a parsed JSON body."""
    if isinstance(data, dict):
        return {
            key: REDACTED
            if key.lower() in SENSITIVE_BODY_KEYS
            else redact_sensitive_fields(value)
            for key, value in data.items()
        }
    if isinstance(data, list):
        return [redact_sensitive_fields(item) for item in data]
    return data


def redact_json_body(decoded: str) -> str:
    """Best-effort: redact sensitive fields if `decoded` is a JSON object/array,
    otherwise return it unchanged (e.g. non-JSON text bodies)."""
    try:
        parsed = json.loads(decoded)
    except Exception:
        return decoded
    return json.dumps(redact_sensitive_fields(parsed))


def truncate_keeping_tail(text: str, limit: int) -> str:
    """Keeps the last `limit` characters instead of the first - for a
    traceback, the exception type/message (the useful part) is at the end,
    while ApiAccessLogRepository.create truncates `detail` by keeping only
    the first 500 characters."""
    return text if len(text) <= limit else text[-limit:]


class LoggerMessage(BaseModel):
    method: str
    url: Any
    host: str | None = None
    type: str = "Request"
    user_email: str | None = None
    status_code: int | None = None
    duration: float | None = None
    response_detail: str | None = None
    request_body: str | None = None

    def __str__(self) -> str:
        short_url = self.url.path
        if self.url.query:
            short_url += "?" + redact_query(self.url.query)
        # A key sent in the URL (rejected, but still logged) must not leak.
        short_url = API_KEY_PATTERN.sub("[REDACTED_API_KEY]", short_url)

        duration_str = f"{self.duration:.3f}" if self.duration is not None else "N/A"

        return (
            f'type="{self.type}" '
            f'host="{self.host if self.host is not None else "N/A"}" '
            f'method="{self.method}" '
            f'path="{short_url}" '
            f'status="{self.status_code if self.status_code is not None else "N/A"}" '
            f'duration="{duration_str}" '  # Usa a string pré-formatada
            f'email="{self.user_email if self.user_email is not None else "N/A"}" '
            f'response_detail="{self.response_detail if self.response_detail is not None else "N/A"}" '
            f'request_body="{self.request_body if self.request_body is not None else "N/A"}"'
        )


class LoggerMiddleware(BaseHTTPMiddleware):
    # One instance serves every concurrent request of the worker, so all
    # per-request state (e.g. the response detail) must stay in locals or in
    # `request.state`, never on `self`.
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    def __get_user_info_from_request(self, request: Request) -> AuthUserInfo | None:
        if hasattr(request.state, "user_info") and isinstance(
            request.state.user_info, AuthUserInfo
        ):
            return request.state.user_info
        return None

    async def __get_request_body(self, request: Request) -> str | None:
        method = request.method
        if method not in LOG_BODY_RULES:
            return None

        start_with = LOG_BODY_RULES[method]["start_with"]
        end_with = LOG_BODY_RULES[method]["end_with"]
        url_path = request.url.path
        if not (
            any(url_path.startswith(prefix) for prefix in start_with)
            and any(url_path.endswith(suffix) for suffix in end_with)
        ):
            return None

        try:
            body = await request.body()

            async def receive() -> dict[str, Any]:
                return {"type": "http.request", "body": body}

            request._receive = receive
            decoded = redact_json_body(body.decode("utf-8"))
        except Exception as e:
            logger.error(f"Error reading request body: {e}")
            return None

        # Cached so `log_response` can attach it to the error-response log
        # line too, not just this (separate) "Request" log line.
        request.state.request_body = decoded
        return decoded

    async def __cache_request_body_for_persistence(self, request: Request) -> None:
        """Bounded, unconditional-but-content-type-gated body capture used
        only for the ApiAccessLog DB row - independent of LOG_BODY_RULES,
        which stays scoped to the text log line above. Skips non-JSON/
        non-text bodies (e.g. file uploads) so binary payloads are never
        buffered in memory."""
        content_type = request.headers.get("content-type", "")
        if not (
            content_type.startswith("application/json")
            or content_type.startswith("text/")
        ):
            return

        try:
            body = await request.body()

            async def receive() -> dict[str, Any]:
                return {"type": "http.request", "body": body}

            request._receive = receive
            decoded = redact_json_body(body.decode("utf-8"))
        except Exception as e:
            logger.error(f"Error reading request body for persistence: {e}")
            return

        request.state.access_log_request_body = decoded

    async def __get_response_detail(
        self, response: Response
    ) -> tuple[Response, str | None]:
        """Reads the body to extract its `message`, returning a copy of the
        response (reading consumes the original) and that detail."""
        if not hasattr(response, "body_iterator"):
            return response, None

        body = b""
        async for chunk in response.body_iterator:  # pyright: ignore[reportAttributeAccessIssue]
            body += chunk

        detail = None
        try:
            json_data = json.loads(body)
            detail = json_data.get("message")
        except Exception:
            pass

        new_response = Response(
            content=body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )
        return new_response, detail

    def __load_user_info_in_message(
        self, message: LoggerMessage, user_info: AuthUserInfo | None
    ) -> None:
        if not user_info:
            return
        message.user_email = user_info.email

    def write_log(self, message: LoggerMessage) -> None:
        logger.info(str(message))

    def __persist_access_log(
        self,
        request: Request,
        response: Response,
        process_time: float,
        detail: str | None,
    ) -> None:
        """Persist a single error-response row (see `__write_access_log`)."""
        if response.status_code < 400:
            return
        # 429s are written by `__persist_rate_limit_event` instead, only for
        # the first hit per IP and window: persisting every rejected request
        # would turn the rate limiter into a database write per hit.
        if response.status_code in (401, 429):
            return
        path = request.url.path
        if any(path.startswith(p) for p in LOKI_EXCLUDED_PATHS):
            return
        self.__write_access_log(
            request,
            status_code=response.status_code,
            extra_tags=[],
            detail=detail,
            process_time=process_time,
        )

    def __persist_rate_limit_event(self, request: Request, process_time: float) -> None:
        """Persist the first request over a rate limit per IP and window,
        flagged by `RateLimitMiddleware`, to keep data for tuning the limits.
        In shadow mode nothing is blocked, so the row records the 429 the
        request would have received, tagged `RateLimit:shadow`."""
        event: RateLimitEvent | None = getattr(
            request.state, RATE_LIMIT_EVENT_STATE_KEY, None
        )
        if event is None:
            return
        detail = f"Rate limit: regra {event.rule} excedida"
        if event.mode == RateLimitMode.SHADOW:
            detail += " (modo shadow, requisição não bloqueada)"
        self.__write_access_log(
            request,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            extra_tags=["RateLimit", f"RateLimit:{event.mode}"],
            detail=detail,
            process_time=process_time,
        )

    def __write_access_log(
        self,
        request: Request,
        *,
        status_code: int,
        extra_tags: list[str],
        detail: str | None,
        process_time: float,
    ) -> None:
        """Best-effort DB write of a single `ApiAccessLog` row. Must never
        raise - a metrics-write failure must not affect the real response.
        Opens a short-lived Session for just this insert+commit (matching
        the per-request pattern in server/db.py's get_db()), NOT a shared
        long-lived session.

        Skipped entirely when CONFIG.testing is set: this always writes via
        server.db.engine directly (the real configured database), not
        through get_db()/dependency_overrides, so it can't be redirected to
        a test database the way route handlers can - running it during the
        test suite would silently write real rows into the dev/prod
        database on every 4xx/5xx a test happens to trigger."""
        if CONFIG.testing:
            return
        try:
            route = request.scope.get("route")
            tags = list(route.tags) if route is not None and route.tags else []
            current_user = getattr(request.state, "current_user", None)
            request_body = getattr(request.state, "access_log_request_body", None)
            identity: ApiKeyIdentity | None = getattr(
                request.state, API_KEY_IDENTITY_STATE_KEY, None
            )
            with Session(engine) as session:
                ApiAccessLogRepository.create(
                    security_level=APISecurityLevel.get_from_tags(tags),
                    endpoint=request.url.path,
                    method=request.method,
                    status_code=status_code,
                    ip_address=get_client_ip(request),
                    user_agent=request.headers.get("user-agent"),
                    response_time_ms=round(process_time * 1000),
                    tags=[*tags, *extra_tags],
                    user_id=current_user.id if current_user else None,
                    detail=detail,
                    request_body=request_body,
                    session=session,
                    api_key_id=identity.key_id if identity else None,
                )
                session.commit()
        except Exception as e:
            logger.error(f"Failed to persist API access log: {e}")

    async def log_request(self, request: Request) -> None:
        msg = LoggerMessage(
            method=request.method,
            url=request.url,
            host=get_client_ip(request),
            duration=request.scope.get("process_time", None),
        )
        info = self.__get_user_info_from_request(request)
        self.__load_user_info_in_message(msg, info)
        msg.request_body = await self.__get_request_body(request)
        self.write_log(msg)

    async def log_response(
        self, request: Request, response: Response, process_time: float
    ) -> Response:
        """Log the response details after the request has been processed.
        This methods returns the original response duplicated because read the body of the response consumes the original response.
        """
        msg = LoggerMessage(
            method=request.method,
            url=request.url,
            host=get_client_ip(request),
            type="Response",
            status_code=response.status_code,
            duration=process_time,
        )
        info = self.__get_user_info_from_request(request)
        self.__load_user_info_in_message(msg, info)
        new_response, detail = await self.__get_response_detail(response)
        msg.response_detail = detail
        self.__persist_access_log(request, response, process_time, detail)
        self.__persist_rate_limit_event(request, process_time)
        if response.status_code >= 400 and hasattr(request.state, "request_body"):
            msg.request_body = request.state.request_body
        self.write_log(msg)
        return new_response

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        await self.__cache_request_body_for_persistence(request)
        # Log the request details
        await self.log_request(request)

        # Call the next middleware or endpoint
        try:
            response: Response = await call_next(request)
        except Exception:
            process_time = time.time() - start_time
            tb = traceback.format_exc()
            logger.error(
                f"Unhandled exception in {request.method} {request.url.path}:\n{tb}"
            )
            response = Response(
                content=json.dumps({"detail": "Internal Server Error"}),
                media_type="application/json",
                status_code=500,
            )
            self.__persist_access_log(
                request, response, process_time, truncate_keeping_tail(tb, 500)
            )
            return response
        process_time = time.time() - start_time

        # Log the response details
        response = await self.log_response(request, response, process_time)

        if request.method == "OPTIONS":
            return response

        path = request.url.path
        if not any(path.startswith(p) for p in LOKI_EXCLUDED_PATHS):
            user_info = self.__get_user_info_from_request(request)
            client_ip = get_client_ip(request)
            loki_access_logger.info(
                "Access Log",
                extra={
                    "client_ip": client_ip if client_ip else "N/A",
                    "method": request.method,
                    "path": path,
                    "status_code": response.status_code,
                    "duration": process_time * 1000,  # ms
                    "email": user_info.email if user_info else "N/A",
                },
            )

        return response
