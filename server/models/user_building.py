from datetime import datetime
from typing import List, Optional
from beanie import Document, Link, Indexed


class User(Document):
    cognito_id: str
    username: Indexed(str, unique=True)
    email: str
    name: str
    is_admin: bool
    created_by: Optional[Link["User"]] = None
    buildings: Optional[List[Link["Building"]]] = None
    updated_at: datetime

    class Settings:
        name = "users"
        keep_nulls = False


class Building(Document):
    name: Indexed(str, unique=True)
    created_by: Link[User]
    updated_at: datetime

    class Settings:
        name = "buildings"
