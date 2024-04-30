from datetime import datetime
from beanie import Document, Link

from user import User

class Building(Document):
    name: str
    created_by: Link[User]
    updated_at: datetime

    class Settings:
        name = "buildings"
