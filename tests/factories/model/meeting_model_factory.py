from datetime import datetime
from typing import Unpack
from sqlmodel import Session
from server.models.database.classroom_db_model import Classroom
from server.models.database.meeting_db_model import Meeting
from server.models.database.user_db_model import User
from server.models.dicts.database.meeting_database_dicts import MeetingModelDict
from server.utils.enums.reservation_type import ReservationType
from server.utils.must_be_int import must_be_int
from tests.factories.base.meeting_base_factory import MeetingBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory
from tests.factories.model.reservation_model_factory import ReservationModelFactory


class MeetingModelFactory(BaseModelFactory[Meeting]):
    def __init__(self, classroom: Classroom, creator: User, session: Session) -> None:
        super().__init__(session)
        self.creator = creator
        self.classroom = classroom
        self.base_factory = MeetingBaseFactory()
        self.faker = self.base_factory.faker
        self.reservation_factory = ReservationModelFactory(
            reservation_type=ReservationType.MEETING,
            creator=creator,
            classroom=classroom,
            session=session,
        )

    def _get_model_type(self) -> type[Meeting]:
        return Meeting

    def get_defaults(self) -> MeetingModelDict:
        base = self.base_factory.get_base_defaults()
        reservation = self.reservation_factory.create_and_refresh()
        return {
            **base,
            "reservation_id": must_be_int(reservation.id),
            "reservation": reservation,
        }

    def create(self, **overrides: Unpack[MeetingModelDict]) -> Meeting:  # type: ignore
        """Create a meeting instance with default values."""
        meeting = super().create(**overrides)

        # Avoid a non-used and inconsistent reservation on database, we delete the
        # reservation created on get_defaults that is call on super().create
        if "reservation" in overrides:
            self.reservation_factory.delete_last_instance()

        return meeting

    def create_and_refresh(self, **overrides: Unpack[MeetingModelDict]) -> Meeting:  # type: ignore
        """Create a meeting instance with default values, commit and refresh it."""
        return super().create_and_refresh(**overrides)

    def update(  # type: ignore
        self, meeting_id: int, **overrides: Unpack[MeetingModelDict]
    ) -> Meeting:
        """Update a meeting instance with default values."""
        meeting = super().update(meeting_id, **overrides)
        meeting.updated_at = datetime.now()
        return meeting

    def update_and_refresh(  # type: ignore
        self, meeting_id: int, **overrides: Unpack[MeetingModelDict]
    ) -> Meeting:
        """Update a meeting, commit the session and return the instance refreshed."""
        meeting = self.update(meeting_id, **overrides)
        self.session.commit()
        self.session.refresh(meeting)
        return meeting
