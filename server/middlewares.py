from collections.abc import Callable
import json
from typing import Any
from fastapi import Request, Response
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from server.models.database.user_db_model import User
from server.logger import logger


class LoggerMessage(BaseModel):
    method: str
    url: str
    type: str = "Request"
    user_id: int | None = None
    user_name: str | None = None
    status_code: int | None = None
    detail: str | None = None

    def __str__(self) -> str:
        return (
            f"{self.type}, "
            f"Method: {self.method}, "
            f"URL: {self.url}, "
            f"User ID: {self.user_id}, "
            f"User Name: {self.user_name}, "
            f"Status Code: {self.status_code}, "
            f"Detail: {self.detail}, "
        )


class LoggerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.detail: Any | None = None

    def __get_user_from_request(self, request: Request) -> User | None:
        if hasattr(request.state, "current_user") and isinstance(
            request.state.current_user, User
        ):
            return request.state.current_user
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

    def __load_user_in_message(self, message: LoggerMessage, user: User | None) -> None:
        if not user:
            return
        message.user_id = user.id
        message.user_name = user.name

    def write_log(self, message: LoggerMessage) -> None:
        logger.info(str(message))

    def log_request(self, request: Request) -> None:
        msg = LoggerMessage(
            method=request.method,
            url=request.url.path,
        )
        user = self.__get_user_from_request(request)
        self.__load_user_in_message(msg, user)
        self.write_log(msg)

    async def log_response(self, request: Request, response: Response) -> Response:
        """Log the response details after the request has been processed.
        This methods returns the original response duplicated because read the body of the response consumes the original response.
        """
        msg = LoggerMessage(
            method=request.method,
            url=request.url.path,
            type="Response",
            status_code=response.status_code,
        )
        user = self.__get_user_from_request(request)
        self.__load_user_in_message(msg, user)
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
