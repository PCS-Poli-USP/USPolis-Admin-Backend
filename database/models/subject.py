from datetime import datetime
from typing import List
from beanie import Document


class Subject(Document):
    subject_code: str
    name: str
    professors: List[str]
    type: str
    class_credit: int
    work_credit: int
    activation: datetime
    desactivation: datetime

    class Settings:
        name = "subjects"  # Colletion Name
