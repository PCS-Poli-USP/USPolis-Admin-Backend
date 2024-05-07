from datetime import datetime
from typing import Annotated, Self

from beanie import Document, Indexed, Link
from fastapi import HTTPException, status


class User(Document):
    username: Annotated[str, Indexed(unique=True)]
    email: str
    is_admin: bool
    name: str
    cognito_id: str
    created_by: Link["User"] | None = None
    buildings: list[Link["Building"]] | None = None  # type: ignore # noqa: F821
    updated_at: datetime

    class Settings:
        name = "users"
        keep_nulls = False

    @classmethod
    async def by_username(cls, username: str) -> Self:
        user = await cls.find_one(cls.username == username)
        if (user is None):
            raise UserNotFound(username)
        return user

    @classmethod
    async def by_id(cls, id: str) -> Self:
        user = await cls.get(id)
        if user is None:
            raise UserNotFound(id)
        return user

    @classmethod
    async def check_username_exists(cls, username: str) -> bool:
        """Check if a username already exists"""
        return await cls.find_one(cls.username == username) is not None


class UserNotFound(HTTPException):
    def __init__(self, user_info: str):
        super().__init__(status.HTTP_404_NOT_FOUND,
                         f"User '{user_info}' not found")
