from datetime import datetime
from pydantic import BaseModel

from server.models.database.reservation_db_model import Reservation

from server.models.http.responses.schedule_response_models import (
    ScheduleResponse,
    ScheduleFullResponse,
)
from server.utils.enums.reservation_type import ReservationType
from server.utils.enums.reservation_status import ReservationStatus
from server.utils.must_be_int import must_be_int


class ReservationResponseBase(BaseModel):
    id: int
    title: str
    type: ReservationType
    reason: str | None
    updated_at: datetime

    building_id: int
    building_name: str

    classroom_id: int | None
    classroom_name: str | None

    schedule_id: int

    created_by_id: int
    created_by: str
    status: ReservationStatus

    requester: str | None
    solicitation_id: int | None

    @classmethod
    def from_reservation(cls, reservation: Reservation) -> "ReservationResponseBase":
        classroom = reservation.get_classroom()
        building = reservation.get_building()
        solicitation = reservation.solicitation
        return cls(
            id=must_be_int(reservation.id),
            title=reservation.title,
            type=reservation.type,
            reason=reservation.reason,
            updated_at=reservation.updated_at,
            building_id=must_be_int(building.id),
            building_name=building.name,
            classroom_id=must_be_int(classroom.id) if classroom else None,
            classroom_name=classroom.name if classroom else None,
            schedule_id=must_be_int(reservation.schedule.id),
            created_by_id=must_be_int(reservation.created_by_id),
            created_by=reservation.created_by.name,
            status=reservation.status,
            requester=solicitation.user.name if solicitation else None,
            solicitation_id=solicitation.id if solicitation else None,
        )


class ReservationResponse(ReservationResponseBase):
    schedule: ScheduleResponse

    @classmethod
    def from_reservation(cls, reservation: Reservation) -> "ReservationResponse":
        base = ReservationResponseBase.from_reservation(reservation)
        return cls(
            **base.model_dump(),
            schedule=ScheduleResponse.from_schedule(reservation.schedule),
        )

    @classmethod
    def from_reservation_list(
        cls, reservations: list[Reservation]
    ) -> list["ReservationResponse"]:
        return [cls.from_reservation(reservation) for reservation in reservations]


class ReservationFullResponse(ReservationResponseBase):
    schedule: ScheduleFullResponse

    @classmethod
    def from_reservation(cls, reservation: Reservation) -> "ReservationFullResponse":
        base = ReservationResponseBase.from_reservation(reservation)
        return cls(
            **base.model_dump(),
            schedule=ScheduleFullResponse.from_schedule(reservation.schedule),
        )

    @classmethod
    def from_reservation_list(
        cls, reservations: list[Reservation]
    ) -> list["ReservationFullResponse"]:
        return [cls.from_reservation(reservation) for reservation in reservations]
