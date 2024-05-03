from datetime import datetime
from typing import Annotated, Optional

from beanie import Document, Indexed, Link


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
<<<<<<< HEAD:server/models/user.py
=======

    @classmethod
    async def by_username(cls, username: str) -> Optional["User"]:
        return await cls.find_one(cls.username == username)
    
>>>>>>> main:server/models/database/user_db_model.py
