from datetime import datetime

from beanie import Document, Link

from server.models.database.holiday_category_db_model import HolidayCategory


class Holiday(Document):
    category: Link[HolidayCategory]
    date: datetime
    type: str
    updated_at: datetime

    class Settings:
        name = "holidays"
