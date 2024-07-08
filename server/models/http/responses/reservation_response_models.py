from datetime import datetime
from pydantic import BaseModel

from server.models.database.reservation_db_model import Reservation
from server.models.http.exceptions.responses_exceptions import UnfetchDataError
from server.models.http.responses.schedule_response_models import ScheduleResponse
from server.utils.enums.reservation_type import ReservationType


class ReservationResponseBase(BaseModel):
    id: int
    name: str
    type: ReservationType
    description: str
    updated_at: datetime


class ReservationResponse(ReservationResponseBase):
    building_id: int
    building_name: str

    classroom_id: int
    classroom_name: str

    schedule_id: int
    schedule: ScheduleResponse

    created_by_id: int
    created_by: str

    @classmethod
    def from_reservation(cls, reservation: Reservation) -> "ReservationResponse":
        if reservation.id is None:
            raise UnfetchDataError("Reservation", "ID")
        if reservation.classroom_id is None:
            raise UnfetchDataError("Reservation", "Classroom ID")
        if reservation.classroom.building_id is None:
            raise UnfetchDataError("Classroom", "Building ID")
        if reservation.classroom.building is None:
            raise UnfetchDataError("Classroom", "Building")
        if reservation.schedule.id is None:
            raise UnfetchDataError("Reservation", "Schedule ID")
        if reservation.created_by_id is None:
            raise UnfetchDataError("Reservation", "User ID")
        return cls(
            id=reservation.id,
            name=reservation.name,
            type=reservation.type,
            description=reservation.description,
            updated_at=reservation.updated_at,
            building_id=reservation.classroom.building_id,
            building_name=reservation.classroom.building.name,
            classroom_id=reservation.classroom_id,
            classroom_name=reservation.classroom.name,
            schedule_id=reservation.schedule.id,
            schedule=ScheduleResponse.from_schedule(reservation.schedule),
            created_by_id=reservation.created_by_id,
            created_by=reservation.created_by.name,
        )

    @classmethod
    def from_reservation_list(
        cls, reservations: list[Reservation]
    ) -> list["ReservationResponse"]:
        return [cls.from_reservation(reservation) for reservation in reservations]
