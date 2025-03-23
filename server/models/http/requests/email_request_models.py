from typing import Self
from pydantic import BaseModel

from server.models.database.classroom_solicitation_db_model import ClassroomSolicitation
from server.models.database.reservation_db_model import Reservation
from server.models.database.user_db_model import User
from server.models.http.requests.classroom_solicitation_request_models import (
    ClassroomSolicitationApprove,
    ClassroomSolicitationDeny,
)
from server.utils.enums.reservation_type import ReservationType


class MailSend(BaseModel):
    to: list[str]
    subject: str
    body: str


class SolicitationMailBase(BaseModel):
    username: str
    title: str
    type: str
    building: str
    classroom: str
    time: str
    dates: str
    capacity: int


class SolicitationDeniedMail(SolicitationMailBase):
    justification: str

    @classmethod
    def from_solicitation(
        cls, input: ClassroomSolicitationDeny, solicitation: ClassroomSolicitation
    ) -> Self:
        str_dates = [date.strftime("%d/%m/%Y") for date in solicitation.dates]
        return cls(
            username=solicitation.user.name,
            title=solicitation.reservation_title,
            type=ReservationType.to_str(solicitation.reservation_type),
            building=solicitation.building.name,
            classroom=solicitation.classroom.name
            if solicitation.classroom
            else "Não informada",
            time=f"{solicitation.start_time.strftime('%H:%M')} ~ {solicitation.end_time.strftime(
                '%H:%M')}"
            if (solicitation.start_time and solicitation.end_time)
            else "Não informado",
            dates=", ".join(str_dates),
            capacity=solicitation.capacity,
            justification=input.justification,
        )


class SolicitationApprovedMail(SolicitationMailBase):
    approved_classroom: str
    approved_time: str

    @classmethod
    def from_solicitation(
        cls, input: ClassroomSolicitationApprove, solicitation: ClassroomSolicitation
    ) -> Self:
        str_dates = [date.strftime("%d/%m/%Y") for date in solicitation.dates]
        return cls(
            username=solicitation.user.name,
            title=solicitation.reservation_title,
            type=ReservationType.to_str(solicitation.reservation_type),
            building=solicitation.building.name,
            classroom=solicitation.classroom.name
            if solicitation.classroom
            else "Não informada",
            time=f"{solicitation.start_time.strftime('%H:%M')} ~ {solicitation.end_time.strftime(
                '%H:%M')}"
            if (solicitation.start_time and solicitation.end_time)
            else "Não informado",
            dates=", ".join(str_dates),
            capacity=solicitation.capacity,
            approved_classroom=input.classroom_name,
            approved_time=f"{input.start_time.strftime('%H:%M')} ~ {
                input.end_time.strftime('%H:%M')}",
        )


class SolicitationRequestedMail(SolicitationMailBase):
    requester: str
    requester_email: str
    reason: str

    @classmethod
    def from_solicitation(cls, user: User, solicitation: ClassroomSolicitation) -> Self:
        str_dates = [date.strftime("%d/%m/%Y") for date in solicitation.dates]
        return cls(
            username=user.name,
            requester=solicitation.user.name,
            requester_email=solicitation.user.email,
            title=solicitation.reservation_title,
            type=ReservationType.to_str(solicitation.reservation_type),
            building=solicitation.building.name,
            classroom=solicitation.classroom.name
            if solicitation.classroom
            else "Não informada",
            time=f"{solicitation.start_time.strftime('%H:%M')} ~ {solicitation.end_time.strftime(
                '%H:%M')}"
            if (solicitation.start_time and solicitation.end_time)
            else "Não informado",
            dates=", ".join(str_dates),
            capacity=solicitation.capacity,
            reason=solicitation.reason if solicitation.reason else "Não informado",
        )


class SolicitationDeletedMail(SolicitationMailBase):
    requester: str
    requester_email: str
    reason: str

    @classmethod
    def from_reservation_and_solicitation(
        cls, solicitation: ClassroomSolicitation, reservation: Reservation
    ) -> Self:
        str_dates = [
            occur.date.strftime("%d/%m/%Y")
            for occur in reservation.schedule.occurrences
        ]
        return cls(
            username=solicitation.user.name,
            requester=reservation.solicitation.user.name
            if reservation.solicitation
            else "Não informado",
            requester_email=reservation.solicitation.user.email
            if reservation.solicitation
            else "Não informado",
            title=reservation.title,
            type=ReservationType.to_str(reservation.type),
            building=reservation.classroom.building.name,
            classroom=reservation.classroom.name,
            time=f"{reservation.schedule.start_time.strftime('%H:%M')} ~ {reservation.schedule.end_time.strftime(
                '%H:%M')}",
            dates=", ".join(str_dates),
            capacity=0,
            reason="Não informado",
        )
