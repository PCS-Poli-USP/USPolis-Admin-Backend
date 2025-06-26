from collections.abc import Callable
import json
from typing import Any
from fastapi import Request, Response
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from server.logger import logger
from server.services.auth.auth_user_info import AuthUserInfo


class LoggerMessage(BaseModel):
    method: str
    url: Any
    host: str | None = None
    type: str = "Request"
    user_email: str | None = None
    user_name: str | None = None
    status_code: int | None = None
    detail: str | None = None

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

    async def __get_response_detail(self, response: Response) -> Response:
        if not hasattr(response, "body_iterator"):
            return response

        body = b""
        async for chunk in response.body_iterator:  # type: ignore
            body += chunk

        detail = None
        try:
            json_data = json.loads(body)
            detail = json_data.get("detail")
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

    def log_request(self, request: Request) -> None:
        msg = LoggerMessage(
            method=request.method,
            url=request.url,
            host=request.client.host if request.client else None,
        )
        info = self.__get_user_info_from_request(request)
        self.__load_user_info_in_message(msg, info)
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
        self.log_request(request)

        # Call the next middleware or endpoint
        response: Response = await call_next(request)

        # Log the response details
        response = await self.log_response(request, response)
        return response
