from datetime import datetime

from pydantic import BaseModel

from server.models.database.institutional_event_db_model import InstitutionalEvent
from server.models.http.exceptions.responses_exceptions import UnfetchDataError
from server.models.http.responses.institutional_event_response_models import InstitutionalEventResponse


class MobileInstitutionalEventResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    start: datetime
    end: datetime
    location: str | None
    building: str | None
    classroom: str | None
    created_at: datetime
    external_link: str | None
    likes: int

    @classmethod
    def from_model(
        cls, event: InstitutionalEvent
    ) -> "InstitutionalEventResponse":
        if event.id is None:
            raise UnfetchDataError("Institutional Event", "ID")
        return cls(
            id=event.id,
            title=event.title,
            description=event.description,
            start=event.start,
            end=event.end,
            location=event.location,
            external_link=event.external_link,
            likes=event.likes,
            category=event.category,
            created_at=event.created_at,
            building=event.building,
            classroom=event.classroom,
        )

    @classmethod
    def from_institutional_event_list(
        cls, events: list[InstitutionalEvent]
    ) -> list["InstitutionalEventResponse"]:
        return [cls.from_model(event) for event in events]

class InstitutionalEventLike(BaseModel):
    event_id: int
    user_id: int
    like: bool