from datetime import datetime
from pydantic import BaseModel

from server.models.database.reservation_db_model import Reservation
from server.models.http.exceptions.responses_exceptions import UnfetchDataError


class ReservationResponseBase(BaseModel):
    id: int
    name: str
    type: str
    description: str
    updated_at: datetime


class ReservationResponse(ReservationResponseBase):
    classroom_id: int
    classroom_name: str

    schedule_id: int

    created_by_id: int
    created_by: str

    @classmethod
    def from_reservation(cls, reservation: Reservation) -> "ReservationResponse":
        if reservation.id is None:
            raise UnfetchDataError("Reservation", "ID")
        if reservation.classroom_id is None:
            raise UnfetchDataError("Reservation", "Classroom ID")
        if reservation.schedule_id is None:
            raise UnfetchDataError("Reservation", "Schedule ID")
        if reservation.created_by_id is None:
            raise UnfetchDataError("Reservation", "User ID")
        return cls(
            id=reservation.id,
            name=reservation.name,
            type=reservation.type,
            description=reservation.description,
            updated_at=reservation.updated_at,
            classroom_id=reservation.classroom_id,
            classroom_name=reservation.classroom.name,
            schedule_id=reservation.schedule_id,
            created_by_id=reservation.created_by_id,
            created_by=reservation.created_by.name,
        )

    @classmethod
    def from_reservation_list(
        cls, reservations: list[Reservation]
    ) -> list["ReservationResponse"]:
        return [cls.from_reservation(reservation) for reservation in reservations]
