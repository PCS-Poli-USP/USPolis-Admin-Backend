import json
import time
from typing import Any
from collections.abc import Callable
from fastapi import Request, Response
from pydantic import BaseModel
from sqlmodel import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from server.db import engine
from server.logger import logger, loki_access_logger
from server.repositories.api_access_log_repository import ApiAccessLogRepository
from server.services.auth.auth_user_info import AuthUserInfo
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


def get_client_ip(request: Request) -> str | None:
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None


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
            short_url += "?" + self.url.query

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
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.detail: Any | None = None

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
            decoded = body.decode("utf-8")
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
            decoded = body.decode("utf-8")
        except Exception as e:
            logger.error(f"Error reading request body for persistence: {e}")
            return

        request.state.access_log_request_body = decoded

    async def __get_response_detail(self, response: Response) -> Response:
        if not hasattr(response, "body_iterator"):
            return response

        body = b""
        async for chunk in response.body_iterator:  # pyright: ignore[reportAttributeAccessIssue]
            body += chunk

        detail = None
        try:
            json_data = json.loads(body)
            detail = json_data.get("message")
        except Exception:
            pass
        self.detail = detail

        return Response(
            content=body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

    def __load_user_info_in_message(
        self, message: LoggerMessage, user_info: AuthUserInfo | None
    ) -> None:
        if not user_info:
            return
        message.user_email = user_info.email

    def write_log(self, message: LoggerMessage) -> None:
        logger.info(str(message))

    def __persist_access_log(
        self, request: Request, response: Response, process_time: float
    ) -> None:
        """Best-effort DB write of a single error-response row. Must never
        raise - a metrics-write failure must not affect the real response.
        Opens a short-lived Session for just this insert+commit (matching
        the per-request pattern in server/db.py's get_db()), NOT a shared
        long-lived session."""
        if response.status_code < 400:
            return
        path = request.url.path
        if any(path.startswith(p) for p in LOKI_EXCLUDED_PATHS):
            return

        try:
            route = request.scope.get("route")
            tags = list(route.tags) if route is not None and route.tags else []
            current_user = getattr(request.state, "current_user", None)
            request_body = getattr(request.state, "access_log_request_body", None)
            with Session(engine) as session:
                ApiAccessLogRepository.create(
                    security_level=APISecurityLevel.get_from_tags(tags),
                    endpoint=path,
                    method=request.method,
                    status_code=response.status_code,
                    ip_address=get_client_ip(request),
                    user_agent=request.headers.get("user-agent"),
                    response_time_ms=round(process_time * 1000),
                    tags=tags,
                    user_id=current_user.id if current_user else None,
                    detail=self.detail,
                    request_body=request_body,
                    session=session,
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
        new_response = await self.__get_response_detail(response)
        msg.response_detail = self.detail
        self.__persist_access_log(request, response, process_time)
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
        response: Response = await call_next(request)
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
