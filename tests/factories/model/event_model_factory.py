from datetime import datetime
from typing import Unpack
from sqlmodel import Session
from server.models.database.classroom_db_model import Classroom
from server.models.database.event_db_model import Event
from server.models.database.user_db_model import User
from server.models.dicts.database.event_database_dicts import EventModelDict
from server.utils.enums.event_type_enum import EventType
from server.utils.enums.reservation_type import ReservationType
from server.utils.must_be_int import must_be_int
from tests.factories.base.event_base_factory import EventBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory
from tests.factories.model.reservation_model_factory import ReservationModelFactory


class EventModelFactory(BaseModelFactory[Event]):
    def __init__(self, classroom: Classroom, creator: User, session: Session) -> None:
        super().__init__(session)
        self.creator = creator
        self.classroom = classroom
        self.base_factory = EventBaseFactory()
        self.faker = self.base_factory.faker
        self.reservation_factory = ReservationModelFactory(
            reservation_type=ReservationType.EVENT,
            creator=creator,
            classroom=classroom,
            session=session,
        )

    def _get_model_type(self) -> type[Event]:
        return Event

    def get_defaults(self) -> EventModelDict:
        base = self.base_factory.get_base_defaults()
        reservation = self.reservation_factory.create_and_refresh()
        return {
            **base,
            "reservation_id": must_be_int(reservation.id),
            "type": self.faker.random_element(EventType.values()),
            "reservation": reservation,
        }

    def create(self, **overrides: Unpack[EventModelDict]) -> Event:  # type: ignore
        """Create a event instance with default values."""
        event = super().create(**overrides)

        # Avoid a non-used and inconsistent reservation on database, we delete the
        # reservation created on get_defaults that is call on super().create
        if "reservation" in overrides:
            self.reservation_factory.delete_last_instance()

        return event

    def create_and_refresh(self, **overrides: Unpack[EventModelDict]) -> Event:  # type: ignore
        """Create a event instance with default values, commit and refresh it."""
        return super().create_and_refresh(**overrides)

    def update(  # type: ignore
        self, event_id: int, **overrides: Unpack[EventModelDict]
    ) -> Event:
        """Update a event instance with default values."""
        event = super().update(event_id, **overrides)
        event.updated_at = datetime.now()
        return event

    def update_and_refresh(  # type: ignore
        self, event_id: int, **overrides: Unpack[EventModelDict]
    ) -> Event:
        """Update a event, commit the session and return the instance refreshed."""
        event = self.update(event_id, **overrides)
        self.session.commit()
        self.session.refresh(event)
        return event
