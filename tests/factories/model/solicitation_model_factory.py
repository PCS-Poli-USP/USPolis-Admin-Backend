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
from tests.factories.model.base_model_factory import BaseModelFactory


class SolicitationModelFactory(BaseModelFactory[Solicitation]):
    def __init__(
        self,
        building: Building,
        user: User,
        reservation: Reservation,
        session: Session,
        solicited_classroom: Classroom | None = None,
    ) -> None:
        super().__init__(session)
        self.building = building
        self.user = user
        self.reservation = reservation
        self.solicited_classroom = solicited_classroom

    def _get_model_type(self) -> type[Solicitation]:
        return Solicitation

    def get_defaults(self) -> SolicitationModelDict:
        return {
            "capacity": 30,
            "required_classroom": self.solicited_classroom is not None,
            "closed_by": None,
            "deleted_by": None,
            "denial_justification": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "building_id": must_be_int(self.building.id),
            "solicited_classroom_id": must_be_int(self.solicited_classroom.id)
            if self.solicited_classroom
            else None,
            "reservation_id": must_be_int(self.reservation.id),
            "user_id": must_be_int(self.user.id),
            "building": self.building,
            "solicited_classroom": self.solicited_classroom,
            "reservation": self.reservation,
            "user": self.user,
        }

    def create(self, **overrides: Unpack[SolicitationModelDict]) -> Solicitation:  # type: ignore
        """Create a solicitation instance with default values."""
        return super().create(**overrides)

    def create_and_refresh(  # type: ignore
        self, **overrides: Unpack[SolicitationModelDict]
    ) -> Solicitation:
        """Create a solicitation instance with default values, commit and refresh it."""
        return super().create_and_refresh(**overrides)

    def update(  # type: ignore
        self, solicitation_id: int, **overrides: Unpack[SolicitationModelDict]
    ) -> Solicitation:
        """Update a solicitation instance with default values."""
        solicitation = super().update(solicitation_id, **overrides)
        solicitation.updated_at = datetime.now()
        return solicitation

    def update_and_refresh(  # type: ignore
        self, solicitation_id: int, **overrides: Unpack[SolicitationModelDict]
    ) -> Solicitation:
        """Update a solicitation, commit the session and return the instance refreshed."""
        solicitation = self.update(solicitation_id, **overrides)
        self.session.commit()
        self.refresh(solicitation)
        return solicitation
