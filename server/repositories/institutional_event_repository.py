from datetime import datetime

from sqlmodel import Session, col, select

from server.models.database.institutional_event_db_model import InstitutionalEvent
from server.models.http.requests.institutional_event_request_models import (
    InstitutionalEventRegister,
)


class InstitutionalEventRepository:
    @staticmethod
    def get_by_id(*, id: int, session: Session) -> InstitutionalEvent:
        statement = select(InstitutionalEvent).where(col(InstitutionalEvent.id) == id)
        event = session.exec(statement).one()
        return event

    @staticmethod
    def get_all(*, session: Session) -> list[InstitutionalEvent]:
        statement = select(InstitutionalEvent)
        events = session.exec(statement).all()
        return list(events)

    @staticmethod
    def create(
        *, input: InstitutionalEventRegister, session: Session
    ) -> InstitutionalEvent:
        new_event = InstitutionalEvent(
            title=input.title,
            description=input.description,
            start=input.start,
            end=input.end,
            location=input.location,
            external_link=input.external_link,
            likes=input.likes,
            category=input.category,
            created_at=datetime.now(),
            building=input.building,
        )
        session.add(new_event)
        session.commit()
        session.refresh(new_event)
        return new_event
