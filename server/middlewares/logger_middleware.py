import json
import time
import traceback
from typing import Any
from collections.abc import Callable
from urllib.parse import unquote_plus
from fastapi import Request, Response, status
from pydantic import BaseModel
from starlette.datastructures import Headers
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from server.config import CONFIG
from server.logger import logger, loki_access_logger
from server.middlewares.request_utils import get_client_ip
from server.services.access_log_writer import ACCESS_LOG_WRITER, AccessLogRow
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
from server.utils.brazil_datetime import BrazilDatetime
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


def _matches_log_body_rules(request: Request) -> bool:
    rules = LOG_BODY_RULES.get(request.method)
    if rules is None:
        return False
    url_path = request.url.path
    return any(url_path.startswith(prefix) for prefix in rules["start_with"]) and any(
        url_path.endswith(suffix) for suffix in rules["end_with"]
    )


def _is_text_content(headers: Headers) -> bool:
    content_type = headers.get("content-type", "")
    return content_type.startswith("application/json") or content_type.startswith(
        "text/"
    )


def _content_length(headers: Headers | Any) -> int | None:
    try:
        return int(headers["content-length"])
    except (KeyError, ValueError, TypeError):
        return None


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

    def __get_user_email(self, request: Request) -> str | None:
        """Who made the request, for the log lines.

        `user_info` is only set by the Bearer-token flow. `current_user` is
        set by every authenticator (session cookie, token, the OVERRIDE_AUTH
        mock), and the cookie is the frontend's only credential, so without
        this fallback almost every line would say email="N/A".
        """
        user_info = getattr(request.state, "user_info", None)
        if isinstance(user_info, AuthUserInfo):
            return user_info.email
        try:
            email = getattr(getattr(request.state, "current_user", None), "email", None)
        except Exception:
            # A detached/expired ORM instance must never break logging.
            return None
        return email if isinstance(email, str) else None

    async def __capture_request_body(self, request: Request) -> None:
        """Reads the raw request body once, when some log line or the
        ApiAccessLog row could use it, and keeps it in
        `request.state.raw_request_body`. Nothing is decoded or parsed here:
        that happens only for a matched LOG_BODY_RULES route or an error
        row (see `__decoded_request_body`), never on every request.

        Bodies over LOG_BODY_MAX_BYTES are never buffered here: when the
        Content-Length says so, the body is left for the endpoint to read."""
        request.state.raw_request_body = None
        if not (_matches_log_body_rules(request) or _is_text_content(request.headers)):
            return
        length = _content_length(request.headers)
        if length is not None and length > CONFIG.log_body_max_bytes:
            return

        try:
            body = await request.body()
        except Exception as e:
            logger.error(f"Error reading request body: {e}")
            return

        async def receive() -> dict[str, Any]:
            return {"type": "http.request", "body": body}

        # The body was consumed: the endpoint gets it from here.
        request._receive = receive
        if len(body) <= CONFIG.log_body_max_bytes:
            request.state.raw_request_body = body

    def __decoded_request_body(self, request: Request) -> str | None:
        """The captured body as redacted text, decoded at most once."""
        if hasattr(request.state, "decoded_request_body"):
            cached: str | None = request.state.decoded_request_body
            return cached
        raw: bytes | None = getattr(request.state, "raw_request_body", None)
        decoded = None
        if raw is not None:
            try:
                decoded = redact_json_body(raw.decode("utf-8"))
            except Exception as e:
                logger.error(f"Error decoding request body: {e}")
        request.state.decoded_request_body = decoded
        return decoded

    def __get_request_body(self, request: Request) -> str | None:
        """Body for the "Request" log line, and for the "Response" one when
        it is an error, for LOG_BODY_RULES routes only."""
        if not _matches_log_body_rules(request):
            return None
        return self.__decoded_request_body(request)

    def __persisted_request_body(self, request: Request) -> str | None:
        """Body for the ApiAccessLog row: JSON/text bodies only, so binary
        payloads (e.g. file uploads) are never stored."""
        if not _is_text_content(request.headers):
            return None
        return self.__decoded_request_body(request)

    async def __get_response_detail(
        self, response: Response
    ) -> tuple[Response, str | None]:
        """For a JSON error response, reads the body to extract its
        `message`, returning a copy of the response (reading consumes the
        original) and that detail. Any other response is passed through
        untouched (and still streamed): buffering and parsing every 2xx
        body just to look for an error message cost CPU on every request."""
        if not hasattr(response, "body_iterator"):
            return response, None
        if response.status_code < 400:
            return response, None
        if not response.headers.get("content-type", "").startswith("application/json"):
            return response, None
        length = _content_length(response.headers)
        if length is not None and length > CONFIG.log_body_max_bytes:
            return response, None

        chunks: list[bytes] = []
        async for chunk in response.body_iterator:  # pyright: ignore[reportAttributeAccessIssue]
            chunks.append(chunk if isinstance(chunk, bytes) else chunk.encode())
        body = b"".join(chunks)

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
            capped=False,
        )

    def __write_access_log(
        self,
        request: Request,
        *,
        status_code: int,
        extra_tags: list[str],
        detail: str | None,
        process_time: float,
        capped: bool = True,
    ) -> None:
        """Queues one `ApiAccessLog` row for the batched writer
        (server/services/access_log_writer.py), which saves it off the event
        loop. Must never raise - a metrics failure must not affect the real
        response. `capped=False` skips the writer's per-client cap.

        Skipped entirely when CONFIG.testing is set: the writer always uses
        server.db.engine directly (the real configured database), not
        get_db()/dependency_overrides, so it can't be redirected to a test
        database the way route handlers can - running it during the test
        suite would silently write real rows into the dev/prod database on
        every 4xx/5xx a test happens to trigger."""
        if CONFIG.testing:
            return
        try:
            route = request.scope.get("route")
            tags = list(route.tags) if route is not None and route.tags else []
            current_user = getattr(request.state, "current_user", None)
            identity: ApiKeyIdentity | None = getattr(
                request.state, API_KEY_IDENTITY_STATE_KEY, None
            )
            row = AccessLogRow(
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
                request_body=None,
                api_key_id=identity.key_id if identity else None,
                timestamp=BrazilDatetime.now_utc(),
            )
            ACCESS_LOG_WRITER.enqueue(
                row,
                capped=capped,
                request_body=lambda: self.__persisted_request_body(request),
            )
        except Exception as e:
            logger.error(f"Failed to queue API access log: {e}")

    async def log_request(self, request: Request) -> None:
        msg = LoggerMessage(
            method=request.method,
            url=request.url,
            host=get_client_ip(request),
            duration=request.scope.get("process_time", None),
        )
        msg.user_email = self.__get_user_email(request)
        msg.request_body = self.__get_request_body(request)
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
        msg.user_email = self.__get_user_email(request)
        new_response, detail = await self.__get_response_detail(response)
        msg.response_detail = detail
        self.__persist_access_log(request, response, process_time, detail)
        self.__persist_rate_limit_event(request, process_time)
        if response.status_code >= 400:
            msg.request_body = self.__get_request_body(request)
        self.write_log(msg)
        return new_response

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        await self.__capture_request_body(request)
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
            email = self.__get_user_email(request)
            client_ip = get_client_ip(request)
            loki_access_logger.info(
                "Access Log",
                extra={
                    "client_ip": client_ip if client_ip else "N/A",
                    "method": request.method,
                    "path": path,
                    "status_code": response.status_code,
                    "duration": process_time * 1000,  # ms
                    "email": email or "N/A",
                },
            )

        return response
