from datetime import datetime
from typing import List, Optional
from beanie import Document, Link, Indexed
from pydantic import BaseModel

from .building import Building

class User(Document):
    cognito_id: str
    username: Indexed(str, unique=True)
    email: str
    name: str
    is_admin: bool
    created_by_id: Link["User"]
    buildings_id: List[Link[Building]]
    updated_at: datetime

    class Settings:
        name = "users"
