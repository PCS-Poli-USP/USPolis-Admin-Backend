from datetime import datetime, time, date
from pydantic import BaseModel

from server.models.database.classroom_solicitation_db_model import ClassroomSolicitation
from server.utils.enums.reservation_type import ReservationType
from server.utils.enums.solicitation_status import SolicitationStatus
from server.utils.must_be_int import must_be_int


class ClassroomSolicitationResponse(BaseModel):
    id: int
    classroom_id: int | None
    classroom: str | None
    required_classroom: bool
    building_id: int
    building: str
    dates: list[date]
    reason: str | None
    reservation_title: str
    reservation_type: ReservationType
    user_id: int
    user: str
    email: str
    start_time: time | None
    end_time: time | None
    capacity: int
    status: SolicitationStatus
    deleted_by: str | None
    closed_by: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_solicitation(
        cls, solicitation: ClassroomSolicitation
    ) -> "ClassroomSolicitationResponse":
        return cls(
            id=must_be_int(solicitation.id),
            classroom_id=solicitation.classroom_id,
            classroom=solicitation.classroom.name if solicitation.classroom else None,
            required_classroom=solicitation.required_classroom,
            building_id=solicitation.building_id,
            building=solicitation.building.name,
            dates=solicitation.dates,
            reason=solicitation.reason,
            reservation_title=solicitation.reservation_title,
            reservation_type=solicitation.reservation_type,
            user_id=solicitation.user_id,
            user=solicitation.user.name,
            email=solicitation.user.email,
            start_time=solicitation.start_time,
            end_time=solicitation.end_time,
            capacity=solicitation.capacity,
            status=solicitation.status,
            deleted_by=solicitation.deleted_by,
            closed_by=solicitation.closed_by,
            created_at=solicitation.created_at,
            updated_at=solicitation.updated_at,
        )

    @classmethod
    def from_solicitation_list(
        cls, solicitations: list[ClassroomSolicitation]
    ) -> list["ClassroomSolicitationResponse"]:
        return [cls.from_solicitation(solicitation) for solicitation in solicitations]
