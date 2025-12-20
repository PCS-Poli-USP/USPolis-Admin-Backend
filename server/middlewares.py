import json
import time
from typing import Any
from collections.abc import Callable
from fastapi import Request, Response
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from server.logger import logger, loki_access_logger
from server.services.auth.auth_user_info import AuthUserInfo


class RoutesDescription(BaseModel):
    method: str
    start_with: str
    end_with: str


ROUTES_LOG_BODY = {
    "GET": {
        "start_with": ["/admin"],
        "end_with": [""],
    },
    "POST": {
        "start_with": ["/admin"],
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
    user_name: str | None = None
    status_code: int | None = None
    duration: float | None = None
    detail: str | None = None
    body: str | None = None

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
            f'user="{self.user_name if self.user_name is not None else "N/A"}" '
            f'email="{self.user_email if self.user_email is not None else "N/A"}" '
            f'detail="{self.detail if self.detail is not None else "N/A"}" '
            f'body="{self.body if self.body is not None else "N/A"}"'
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
        if method in ROUTES_LOG_BODY:
            start_with = ROUTES_LOG_BODY[method]["start_with"]
            end_with = ROUTES_LOG_BODY[method]["end_with"]
            url_path = request.url.path

            if any(url_path.startswith(prefix) for prefix in start_with) and any(
                url_path.endswith(suffix) for suffix in end_with
            ):
                try:
                    body = await request.body()

                    async def receive() -> dict[str, Any]:
                        return {"type": "http.request", "body": body}

                    request._receive = receive
                    return body.decode("utf-8")
                except Exception as e:
                    logger.error(f"Error reading request body: {e}")
        return None

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
        message.user_name = user_info.name

    def write_log(self, message: LoggerMessage) -> None:
        logger.info(str(message))

    async def log_request(self, request: Request) -> None:
        msg = LoggerMessage(
            method=request.method,
            url=request.url,
            host=get_client_ip(request),
            duration=request.scope.get("process_time", None),
        )
        info = self.__get_user_info_from_request(request)
        self.__load_user_info_in_message(msg, info)
        msg.body = await self.__get_request_body(request)
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
        msg.detail = self.detail
        self.write_log(msg)
        return new_response

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        # Log the request details
        await self.log_request(request)
        process_time = time.time() - start_time

        # Call the next middleware or endpoint
        response: Response = await call_next(request)

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
                    "user": user_info.name if user_info else "N/A",
                    "email": user_info.email if user_info else "N/A",
                },
            )

        return response
