from collections.abc import Callable
from enum import Enum
import json
from typing import Any
from fastapi import APIRouter, Request, Response
from fastapi.routing import APIRoute
from pydantic import BaseModel
from sqlmodel import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from time import time
from datetime import datetime

from server.logger import logger
from server.models.database.api_access_log import APIAccessLog
from server.models.database.user_db_model import User
from server.services.auth.auth_user_info import AuthUserInfo
from server.utils.enums.api_access_log_enums import APISecurityLevel


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


class LoggerMessage(BaseModel):
    method: str
    url: Any
    host: str | None = None
    type: str = "Request"
    user_email: str | None = None
    user_name: str | None = None
    status_code: int | None = None
    detail: str | None = None
    body: str | None = None

    def __str__(self) -> str:
        short_url = self.url.path + self.url.query if self.url.query else self.url.path
        return (
            f"{self.type}, "
            f"Host: {self.host}, "
            f"Method: {self.method}, "
            f"URL: {short_url}, "
            f"Email: {self.user_email}, "
            f"Name: {self.user_name}, "
            f"Code: {self.status_code}, "
            f"Detail: {self.detail}, "
            f"Body: {self.body}"
        )


class LoggerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, session: Session) -> None:
        super().__init__(app)
        self.router: APIRouter = getattr(getattr(app, "app"), "app")
        self.session = session
        self.detail: Any | None = None
        routes = [route for route in self.router.routes if isinstance(route, APIRoute)]
        self.route_tags_map = {
            route.path: route.tags if route.tags else [] for route in routes
        }

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
            host=request.client.host if request.client else None,
        )
        info = self.__get_user_info_from_request(request)
        self.__load_user_info_in_message(msg, info)
        msg.body = await self.__get_request_body(request)
        self.write_log(msg)

    async def log_response(self, request: Request, response: Response) -> Response:
        """Log the response details after the request has been processed.
        This methods returns the original response duplicated because read the body of the response consumes the original response.
        """
        msg = LoggerMessage(
            method=request.method,
            url=request.url,
            host=request.client.host if request.client else None,
            type="Response",
            status_code=response.status_code,
        )
        info = self.__get_user_info_from_request(request)
        self.__load_user_info_in_message(msg, info)
        new_response = await self.__get_response_detail(response)
        msg.detail = self.detail
        self.write_log(msg)
        return new_response

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log the request details
        await self.log_request(request)

        start_time = time()
        # Call the next middleware or endpoint
        response: Response = await call_next(request)
        end_time = time()

        tags: list[str | Enum] = []
        route = request.scope.get("route")
        if route:
            path_template = route.path
            tags = self.route_tags_map.get(path_template, [])

        current_user: User | None = (
            request.state.current_user
            if hasattr(request.state, "current_user")
            else None
        )

        api_access_log = APIAccessLog(
            security_level=APISecurityLevel.get_from_tags(tags).value,  # type: ignore
            endpoint=request.url.path,
            method=request.method,
            status_code=response.status_code,
            timestamp=datetime.fromtimestamp(start_time),
            ip_address=request.client.host if request.client else None,
            response_time_ms=(end_time - start_time) * 1000,
            tags=tags,  # type: ignore
            user_agent=request.headers.get("user-agent", ""),
            user_id=current_user.id if current_user else None,
        )
        self.session.add(api_access_log)
        self.session.commit()
        # Log the response details
        response = await self.log_response(request, response)
        return response
