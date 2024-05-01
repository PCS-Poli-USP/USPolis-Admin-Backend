from datetime import datetime
from typing import List, Optional
from beanie import Document, Link
from pydantic import BaseModel

from database.models.subject import Subject

class Preferences(BaseModel):
    air_conditionating: bool
    accessibility: bool
    projector: bool

class Class(Document):
    subject: Link[Subject]
    period: List[str]
    start_date: datetime
    end_date: datetime
    class_type: str
    vacancies: int
    subscribers: int
    pendings: int
    preferences: Preferences
    ignore_to_allocate: Optional[bool]
    full_allocated: Optional[bool]
    updated_at: datetime
    # creted_by: Link[User]
    # schedule: Link[Schedule]