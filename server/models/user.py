from datetime import datetime
from typing import Annotated, Optional

from beanie import Document, Indexed, Link
from pydantic import BaseModel


class UserRegister(BaseModel):
    username: str
    email: str
    name: str
    is_admin: bool
    buildings: list[str] | None = None


class User(Document, UserRegister):
    username: Annotated[str, Indexed(unique=True)]
    cognito_id: str
    created_by: Link["User"] | None = None
    buildings: list[Link["Building"]] | None = None  # type: ignore # noqa: F821
    updated_at: datetime

    class Settings:
        name = "users"
        keep_nulls = False
    
    @classmethod
    async def by_username(cls, username: str) -> Optional["User"]:
        return await cls.find_one(cls.username == username)