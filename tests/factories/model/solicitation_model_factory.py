from datetime import datetime
from typing import Unpack

from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.reservation_db_model import Reservation
from server.models.database.solicitation_db_model import Solicitation
from server.models.database.user_db_model import User
from server.models.dicts.database.solicitation_database_dicts import (
    SolicitationModelDict,
)
from server.utils.must_be_int import must_be_int
from tests.factories.base.solicitation_base_factory import SolicitationBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory


class SolicitationModelFactory(BaseModelFactory[Solicitation]):
    """Solicitation for an existing reservation. Pass `solicited_classroom` to
    ask for a specific classroom; by default none is chosen."""

    def __init__(
        self,
        building: Building,
        requester: User,
        reservation: Reservation,
        session: Session,
        solicited_classroom: Classroom | None = None,
    ) -> None:
        super().__init__(session)
        self.building = building
        self.requester = requester
        self.reservation = reservation
        self.solicited_classroom = solicited_classroom
        self.core_factory = SolicitationBaseFactory(must_be_int(building.id))

    def _get_model_type(self) -> type[Solicitation]:
        return Solicitation

    def get_defaults(self) -> SolicitationModelDict:
        core = self.core_factory.get_base_defaults()
        classroom = self.solicited_classroom
        return {
            **core,
            # The DB requires a solicited classroom when it is required.
            "required_classroom": core["required_classroom"] and classroom is not None,
            "closed_by": None,
            "deleted_by": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "solicited_classroom_id": classroom.id if classroom else None,
            "reservation_id": must_be_int(self.reservation.id),
            "user_id": must_be_int(self.requester.id),
            "building": self.building,
            "solicited_classroom": classroom,
            "reservation": self.reservation,
            "user": self.requester,
        }

    def create(self, **overrides: Unpack[SolicitationModelDict]) -> Solicitation:  # type: ignore
        """Create a solicitation instance with default values."""
        return super().create(**overrides)

    def create_and_refresh(  # type: ignore
        self, **overrides: Unpack[SolicitationModelDict]
    ) -> Solicitation:
        """Create a solicitation instance with default values, commit and refresh it."""
        return super().create_and_refresh(**overrides)
