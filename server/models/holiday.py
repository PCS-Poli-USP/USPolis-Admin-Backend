from beanie import Document, Link
from datetime import datetime

from database.models.holiday_category import HolidayCategory


class Holiday(Document):
    category = Link[HolidayCategory]
    date = datetime
    type = str
    updated_at = datetime

    class Settings:
        name = "holidays"
