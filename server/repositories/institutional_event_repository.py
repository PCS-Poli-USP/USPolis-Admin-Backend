from fastapi import HTTPException, status
from sqlmodel import Session, col, select

from server.models.database.institutional_event_db_model import InstitutionalEvent
from server.models.database.user_db_model import User
from server.models.http.requests.institutional_event_request_models import (
    InstitutionalEventRegister,
    InstitutionalEventUpdate,
)
from server.utils.brazil_datetime import BrazilDatetime


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
        *, creator: User, input: InstitutionalEventRegister, session: Session
    ) -> InstitutionalEvent:
        new_event = InstitutionalEvent(
            title=input.title,
            description=input.description,
            start=input.start,
            end=input.end,
            location=input.location,
            external_link=input.external_link,
            category=input.category,
            created_at=BrazilDatetime.now_utc(),
            building=input.building,
            classroom=input.classroom,
            created_by_id=creator.id,
        )
        session.add(new_event)
        session.commit()
        session.refresh(new_event)
        return new_event

    @staticmethod
    def update(
        *, id: int, input: InstitutionalEventUpdate, user: User, session: Session
    ) -> InstitutionalEvent:
        event = InstitutionalEventRepository.get_by_id(id=id, session=session)
        InstitutionalEventRepository._check_creator_or_admin(event, user, "editar")
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
    def save_likes(*, event: InstitutionalEvent, session: Session) -> None:
        session.add(event)
        session.commit()

    @staticmethod
    def delete(*, id: int, user: User, session: Session) -> None:
        event = InstitutionalEventRepository.get_by_id(id=id, session=session)
        InstitutionalEventRepository._check_creator_or_admin(event, user, "excluir")
        session.delete(event)
        session.commit()

    @staticmethod
    def _check_creator_or_admin(
        event: InstitutionalEvent, user: User, verb: str
    ) -> None:
        """Only the creator or an admin changes an event (an event with no
        recorded creator: admins only)."""
        if user.is_admin:
            return
        if event.created_by_id is None or event.created_by_id != user.id:
            raise InstitutionalEventOperationNotAllowed(verb, event.title)


class InstitutionalEventOperationNotAllowed(HTTPException):
    def __init__(self, verb: str, title: str) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Só quem criou o evento institucional {title} ou um "
                f"administrador pode {verb} o evento"
            ),
        )
