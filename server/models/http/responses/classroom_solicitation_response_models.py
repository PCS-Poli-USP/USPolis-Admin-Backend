from datetime import datetime, time, date as date_type
from pydantic import BaseModel

from server.models.database.classroom_solicitation_db_model import ClassroomSolicitation
from server.utils.enums.reservation_type import ReservationType
from server.utils.must_be_int import must_be_int


class ClassroomSolicitationResponse(BaseModel):
    id: int
    classroom_id: int
    classroom: str
    building_id: int
    building: str
    date: date_type
    reason: str
    reservation_type: ReservationType
    email: str
    start_time: time
    end_time: time
    capacity: int
    approved: bool
    denied: bool
    closed: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_solicitation(
        cls, solicitation: ClassroomSolicitation
    ) -> "ClassroomSolicitationResponse":
        return cls(
            id=must_be_int(solicitation.id),
            classroom_id=solicitation.classroom_id,
            classroom=solicitation.classroom.name,
            building_id=solicitation.building_id,
            building=solicitation.building.name,
            date=solicitation.date,
            reason=solicitation.reason,
            reservation_type=solicitation.reservation_type,
            email=solicitation.email,
            start_time=solicitation.start_time,
            end_time=solicitation.end_time,
            capacity=solicitation.capacity,
            approved=solicitation.approved,
            denied=solicitation.denied,
            closed=solicitation.closed,
            created_at=solicitation.created_at,
            updated_at=solicitation.updated_at,
        )

    @classmethod
    def from_solicitation_list(
        cls, solicitations: list[ClassroomSolicitation]
    ) -> list["ClassroomSolicitationResponse"]:
        return [cls.from_solicitation(solicitation) for solicitation in solicitations]
