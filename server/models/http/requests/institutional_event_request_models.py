from datetime import datetime

from pydantic import BaseModel


class InstitutionalEventRegister(BaseModel):
    title: str
    description: str
    start: datetime
    end: datetime
    category: str
    building: str | None = None
    classroom: str | None = None
    location: str | None = None
    external_link: str | None = None


class InstitutionalEventUpdate(InstitutionalEventRegister):
    pass
