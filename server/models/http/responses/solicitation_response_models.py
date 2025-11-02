from datetime import datetime
from pydantic import BaseModel

from server.models.database.solicitation_db_model import (
    Solicitation,
)
from server.utils.enums.reservation_status import ReservationStatus
from server.utils.must_be_int import must_be_int
from server.models.http.responses.reservation_response_models import ReservationResponse


class SolicitationResponse(BaseModel):
    id: int
    capacity: int
    required_classroom: bool
    status: ReservationStatus
    closed_by: str | None
    deleted_by: str | None
    created_at: datetime
    updated_at: datetime

    user_id: int
    user: str
    email: str

    building_id: int
    building: str

    reservation: ReservationResponse

    @classmethod
    def from_solicitation(cls, solicitation: Solicitation) -> "SolicitationResponse":
        return cls(
            id=must_be_int(solicitation.id),
            capacity=solicitation.capacity,
            required_classroom=solicitation.required_classroom,
            status=solicitation.get_status(),
            closed_by=solicitation.closed_by,
            deleted_by=solicitation.deleted_by,
            created_at=solicitation.created_at,
            updated_at=solicitation.updated_at,
            building_id=solicitation.building_id,
            building=solicitation.building.name,
            user_id=solicitation.user_id,
            user=solicitation.user.name,
            email=solicitation.user.email,
            reservation=ReservationResponse.from_reservation(solicitation.reservation),
        )

    @classmethod
    def from_solicitation_list(
        cls, solicitations: list[Solicitation]
    ) -> list["SolicitationResponse"]:
        return [cls.from_solicitation(solicitation) for solicitation in solicitations]
