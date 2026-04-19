from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint
from sqlmodel import Field, Relationship, SQLModel


if TYPE_CHECKING:
    from server.models.database.user_absence import UserAbsence

from server.utils.brazil_datetime import BrazilDatetime


class UserScheduleEntry(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint(
            "absence_count >= 0",
            name="user_schedule_check_absence_count_non_negative",
        ),
    )

    user_schedule_id: int = Field(foreign_key="user_schedule.id", index=True)
    schedule_id: int = Field(foreign_key="schedule.id", index=True)

    absence_count: int = Field(default=0)
    updated_at: BrazilDatetime = Field(default_factory=BrazilDatetime.now_utc)
    created_at: BrazilDatetime = Field(default_factory=BrazilDatetime.now_utc)

    absences: list["UserAbsence"] = Relationship(back_populates="entries")
