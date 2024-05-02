from datetime import datetime
from typing import Annotated

from beanie import Document, Indexed, Link
from pydantic import BaseModel


class UserRegister(BaseModel):
    username: str
    email: str
    name: str
    is_admin: bool
    buildings: list[Link["Building"]] | None = None  # type: ignore # noqa: F821


class User(Document):
    cognito_id: str
    username: Annotated[str, Indexed(unique=True)]
    email: str
    name: str
    is_admin: bool
    created_by: Link["User"] | None = None
    buildings: list[Link["Building"]] | None = None  # type: ignore # noqa: F821
    updated_at: datetime

    class Settings:
        name = "users"
        keep_nulls = False
