from typing import Self
from pydantic import BaseModel

from server.models.database.classroom_solicitation_db_model import ClassroomSolicitation
from server.models.http.requests.classroom_solicitation_request_models import (
    ClassroomSolicitationApprove,
    ClassroomSolicitationDeny,
)
from server.utils.enums.reservation_type import ReservationType


class MailSend(BaseModel):
    to: list[str]
    subject: str
    body: str


class BCCMailSend(BaseModel):
    bcc_list: list[str]
    subject: str
    body: str


class SolicitationMailBase(BaseModel):
    title: str
    type: str
    building: str
    classroom: str
    time: str
    dates: str
    capacity: int

    @classmethod
    def from_solicitation(cls, solicitation: ClassroomSolicitation) -> Self:
        str_dates = [date.strftime("%d/%m/%Y") for date in solicitation.dates]
        return cls(
            title=solicitation.reservation_title,
            type=ReservationType.to_str(solicitation.reservation_type),
            building=solicitation.building.name,
            classroom=solicitation.classroom.name
            if solicitation.classroom
            else "Não informada",
            time=f"{solicitation.start_time.strftime('%H:%M')} ~ {
                solicitation.end_time.strftime('%H:%M')
            }"
            if (solicitation.start_time and solicitation.end_time)
            else "Não informado",
            dates=", ".join(str_dates),
            capacity=solicitation.capacity,
        )


class SolicitationDeniedMail(SolicitationMailBase):
    username: str
    justification: str

    @classmethod
    def from_solicitation(  # type: ignore
        cls, input: ClassroomSolicitationDeny, solicitation: ClassroomSolicitation
    ) -> "SolicitationDeniedMail":
        base = SolicitationMailBase.from_solicitation(solicitation)
        return cls(
            **base.model_dump(),
            username=solicitation.user.name,
            justification=input.justification,
        )


class SolicitationApprovedMail(SolicitationMailBase):
    username: str
    approved_classroom: str
    approved_time: str

    @classmethod
    def from_solicitation(  # type: ignore
        cls, input: ClassroomSolicitationApprove, solicitation: ClassroomSolicitation
    ) -> Self:
        base = SolicitationMailBase.from_solicitation(solicitation)
        return cls(
            **base.model_dump(),
            username=solicitation.user.name,
            approved_classroom=input.classroom_name,
            approved_time=f"{input.start_time.strftime('%H:%M')} ~ {
                input.end_time.strftime('%H:%M')
            }",
        )


class SolicitationRequestedMail(SolicitationMailBase):
    requester: str
    requester_email: str
    reason: str

    @classmethod
    def from_solicitation(cls, solicitation: ClassroomSolicitation) -> Self:
        base = SolicitationMailBase.from_solicitation(solicitation)
        return cls(
            **base.model_dump(),
            requester=solicitation.user.name,
            requester_email=solicitation.user.email,
            reason=solicitation.reason if solicitation.reason else "Não informado",
        )


class SolicitationDeletedMail(SolicitationMailBase):
    username: str

    @classmethod
    def from_solicitation(
        cls, solicitation: ClassroomSolicitation
    ) -> "SolicitationDeletedMail":
        base = SolicitationMailBase.from_solicitation(solicitation)
        return cls(
            **base.model_dump(),
            username=solicitation.user.name,
        )


class SolicitationCancelledMail(SolicitationRequestedMail):
    pass
