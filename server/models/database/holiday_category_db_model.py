from beanie import Document


class HolidayCategory(Document):
    category: str

    class Settings:
        name = "holiday_categories"
