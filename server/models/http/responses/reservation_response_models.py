from pydantic import BaseModel

from server.models.database.reservation_db_model import Reservation


class ReservationResponse(BaseModel):
    @classmethod
    def from_reservation(cls, reservation: Reservation) -> "ReservationResponse":
        return cls()

    @classmethod
    def from_reservation_list(
        cls, reservations: list[Reservation]
    ) -> list["ReservationResponse"]:
        return [cls.from_reservation(reservation) for reservation in reservations]
