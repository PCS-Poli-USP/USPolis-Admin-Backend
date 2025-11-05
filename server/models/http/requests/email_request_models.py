from typing import Self
from pydantic import BaseModel

from server.models.database.solicitation_db_model import (
    Solicitation,
)
from server.models.http.requests.solicitation_request_models import (
    SolicitationApprove,
    SolicitationDeny,
)
from server.utils.enums.month_week import MonthWeek
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.reservation_type import ReservationType
from server.utils.enums.week_day import WeekDay
from server.utils.occurrence_utils import OccurrenceUtils


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
    capacity: int
    recurrence: Recurrence
    week_day: WeekDay | None
    month_week: MonthWeek | None
    dates: str

    @classmethod
    def from_solicitation(cls, solicitation: Solicitation) -> Self:
        schedule = solicitation.reservation.schedule
        str_dates = [
            dt.strftime("%d/%m/%Y") for dt in OccurrenceUtils.generate_dates(schedule)
        ]
        classroom = solicitation.solicited_classroom
        return cls(
            title=solicitation.reservation.title,
            type=ReservationType.to_str(solicitation.reservation.type),
            building=solicitation.building.name,
            classroom=classroom.name if classroom else "Não especificada",
            capacity=solicitation.capacity,
            recurrence=schedule.recurrence,
            week_day=schedule.week_day,
            month_week=schedule.month_week,
            time=f"{schedule.start_time.strftime('%H:%M')} ~ {schedule.end_time.strftime('%H:%M')}",
            dates=", ".join(str_dates),
        )


class SolicitationDeniedMail(SolicitationMailBase):
    username: str
    justification: str

    @classmethod
    def from_solicitation(  # type: ignore
        cls, input: SolicitationDeny, solicitation: Solicitation
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

    @classmethod
    def from_solicitation(  # type: ignore
        cls,
        input: SolicitationApprove,
        solicitation: Solicitation,
    ) -> Self:
        base = SolicitationMailBase.from_solicitation(solicitation)
        return cls(
            **base.model_dump(),
            username=solicitation.user.name,
            approved_classroom=input.classroom_name,
        )


class SolicitationRequestedMail(SolicitationMailBase):
    requester: str
    requester_email: str
    reason: str

    @classmethod
    def from_solicitation(cls, solicitation: Solicitation) -> Self:
        base = SolicitationMailBase.from_solicitation(solicitation)
        reason = (
            solicitation.reservation.reason
            if solicitation.reservation.reason
            else "Não informado"
        )
        return cls(
            **base.model_dump(),
            requester=solicitation.user.name,
            requester_email=solicitation.user.email,
            reason=reason,
        )


class SolicitationDeletedMail(SolicitationMailBase):
    username: str

    @classmethod
    def from_solicitation(cls, solicitation: Solicitation) -> "SolicitationDeletedMail":
        base = SolicitationMailBase.from_solicitation(solicitation)
        return cls(
            **base.model_dump(),
            username=solicitation.user.name,
        )


class SolicitationCancelledMail(SolicitationRequestedMail):
    pass
