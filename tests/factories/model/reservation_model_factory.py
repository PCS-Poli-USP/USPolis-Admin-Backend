from datetime import datetime
from typing import Unpack
from sqlmodel import Session
from server.models.database.classroom_db_model import Classroom
from server.models.database.reservation_db_model import Reservation
from server.models.database.user_db_model import User
from server.models.dicts.database.reservation_database_dicts import ReservationModelDict
from server.utils.enums.audiovisual_type_enum import AudiovisualType
from server.utils.enums.reservation_status import ReservationStatus
from server.utils.enums.reservation_type import ReservationType
from server.utils.must_be_int import must_be_int
from tests.factories.base.reservation_base_factory import ReservationBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory


class ReservationModelFactory(BaseModelFactory[Reservation]):
    def __init__(
        self,
        reservation_type: ReservationType,
        creator: User,
        classroom: Classroom,
        session: Session,
    ) -> None:
        super().__init__(session)
        self.reservation_type = reservation_type
        self.creator = creator
        self.classroom = classroom
        self.core_factory = ReservationBaseFactory(reservation_type=reservation_type)
        self.faker = self.core_factory.faker

    def _get_model_type(self) -> type[Reservation]:
        return Reservation

    def get_defaults(self) -> ReservationModelDict:
        """Create a default dict values for Reservation, by default the values are:\n
        - status = Pending
        - schedule = None (must be a reservation before)
        - solicitation = None (same as above)
        - exam = None (same as above)
        - event = None (same as above)
        - meeting = None (same as above)
        """
        base = self.core_factory.get_base_defaults()
        return {
            **base,
            "updated_at": datetime.now(),
            "audiovisual": self.faker.random_element(AudiovisualType.values()),
            "created_by_id": must_be_int(self.creator.id),
            "status": ReservationStatus.PENDING,
            "created_by": self.creator,
            "solicitation": None,
            "exam": None,
            "event": None,
            "meeting": None,
        }

    def create(self, **overrides: Unpack[ReservationModelDict]) -> Reservation:  # type: ignore
        """Create a reservation instance with default values."""
        return super().create(**overrides)

    def create_and_refresh(  # type: ignore
        self, **overrides: Unpack[ReservationModelDict]
    ) -> Reservation:
        """Create a reservation instance with default values, commit and refresh it."""
        return super().create_and_refresh(**overrides)

    def update(  # type: ignore
        self, reservation_id: int, **overrides: Unpack[ReservationModelDict]
    ) -> Reservation:
        """Update a reservation instance with default values."""
        reservation = super().update(reservation_id, **overrides)
        reservation.updated_at = datetime.now()
        return reservation

    def update_and_refresh(  # type: ignore
        self, reservation_id: int, **overrides: Unpack[ReservationModelDict]
    ) -> Reservation:
        """Update a reservation, commit the session and return the instance refreshed."""
        reservation = self.update(reservation_id, **overrides)
        self.session.commit()
        self.session.refresh(reservation)
        return reservation
