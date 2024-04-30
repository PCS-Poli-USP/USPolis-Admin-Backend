from datetime import datetime
from typing import List
from beanie import Document, Link

from database.models.user_building import Building


class Subject(Document):
    buildings: List[Link[Building]]
    code: str
    name: str
    professors: List[str]
    type: str
    class_credit: int
    work_credit: int
    activation: datetime
    desactivation: datetime

    class Settings:
        name = "subjects"  # Colletion Name
