from datetime import datetime

from beanie import Document


class InstitutionalEvent(Document):
    title: str
    description: str
    start: datetime
    end: datetime | None
    location: str
    external_link: str
    likes: int
    category: str
    created_at: str
    building: str

    class Settings:
        name = "institutional_events"
        keep_nulls = False
