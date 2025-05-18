from datetime import datetime

from sqlmodel import Session, col, select

from server.models.database.institutional_event_db_model import InstitutionalEvent
from server.models.http.requests.institutional_event_request_models import (
    InstitutionalEventRegister,
    InstitutionalEventUpdate,
)
from server.utils.brasil_datetime import BrasilDatetime


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
            category=input.category,
            created_at=BrasilDatetime.now_utc(),
            building=input.building,
            classroom=input.classroom,
        )
        session.add(new_event)
        session.commit()
        session.refresh(new_event)
        return new_event

    @staticmethod
    def update(
        *, id: int, input: InstitutionalEventUpdate, session: Session
    ) -> InstitutionalEvent:
        event = InstitutionalEventRepository.get_by_id(id=id, session=session)
        event.title = input.title
        event.description = input.description
        event.start = input.start
        event.end = input.end
        event.location = input.location
        event.external_link = input.external_link
        event.category = input.category
        event.building = input.building
        event.classroom = input.classroom
        session.add(event)
        session.commit()
        return event

    @staticmethod
    def delete(*, id: int, session: Session) -> None:
        event = InstitutionalEventRepository.get_by_id(id=id, session=session)
        session.delete(event)
        session.commit()
