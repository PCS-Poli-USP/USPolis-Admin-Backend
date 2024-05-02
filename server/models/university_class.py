from datetime import datetime
from beanie import Document, Link
from pydantic import BaseModel

from server.models.subject import Subject
from server.models.user import User
from server.models.schedule import Schedule


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
