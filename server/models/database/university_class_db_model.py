from datetime import datetime
from beanie import Document, Link
from pydantic import BaseModel

from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.models.database.schedule_db_model import Schedule


class Preferences(BaseModel):
    air_conditionating: bool
    accessibility: bool
    projector: bool


class Class(Document):
    subject: Link[Subject]
    period: list[str]
    start_period: datetime
    end_period: datetime
    class_type: str
    vacancies: int
    subscribers: int
    pendings: int
    preferences: Preferences
    ignore_to_allocate: bool | None = None
    full_allocated: bool | None = None
    updated_at: datetime
    creted_by: Link[User]
    schedule: Link[Schedule]

    class Settings:
        name = "classes"  # Colletion Name
        keep_nulls = False
