from datetime import datetime

from pydantic import BaseModel


class InstitutionalEventRegister(BaseModel):
    title: str
    description: str
    start: datetime
    end: datetime | None
    location: str
    external_link: str
    likes: int
    category: str
    building: str


class InstitutionalEventUpdate(InstitutionalEventRegister):
    pass
