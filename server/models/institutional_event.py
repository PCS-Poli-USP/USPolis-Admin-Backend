from beanie import Document
from datetime import datetime
from typing import Optional


class InstitutionalEvent(Document):
    title = str
    description = str
    start = datetime
    end = Optional[datetime] = None
    location = str
    external_link = str
    likes = int
    category = str
    created_at = str
    building = str

    class Settings:
        name = 'institutional_events'
        keep_nulls = False
