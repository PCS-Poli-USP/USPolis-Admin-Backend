from datetime import datetime

from pydantic import BaseModel

from server.models.database.institutional_event_db_model import InstitutionalEvent
from server.models.http.exceptions.responses_exceptions import UnfetchDataError
from server.models.http.requests.institutional_event_request_models import (
    InstitutionalEventUpdate,
)


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
    ) -> "MobileInstitutionalEventResponse":
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
    ) -> list["MobileInstitutionalEventResponse"]:
        return [cls.from_model(event) for event in events]


def to_event_update(cls: InstitutionalEvent) -> InstitutionalEventUpdate:
    return InstitutionalEventUpdate(
        title=cls.title,
        description=cls.description,
        start=cls.start,
        end=cls.end,
        category=cls.category,
        building=cls.building,
        classroom=cls.classroom,
        location=cls.location,
        external_link=cls.external_link,
    )


class MobileInstitutionalEventLike(BaseModel):
    event_id: int
    user_id: int
    like: bool
