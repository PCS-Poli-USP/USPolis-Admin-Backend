from datetime import datetime
from beanie import Document, Link

from server.models.database.building_db_model import Building


class Subject(Document):
    buildings: list[Link[Building]]
    code: str
    name: str
    professors: list[str]
    type: str
    class_credit: int
    work_credit: int
    activation: datetime
    desactivation: datetime

    class Settings:
        name = "subjects"  # Colletion Name
