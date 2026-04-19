from datetime import date
from typing import TYPE_CHECKING
from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field

from server.models.database.base_db_model import BaseModel

if TYPE_CHECKING:
    from server.models.database.user_schedule_entry_db_model import UserScheduleEntry

from server.utils.brazil_datetime import BrazilDatetime


class UserAbsence(BaseModel):
    __table_args__ = (
        UniqueConstraint(
            "user_schedule_id",
            "schedule_id",
            "absence_date",
            name="user_absence_unique_entry_date",
        ),
        Index(
            "user_absence_entry_idx",
            "user_schedule_id",
            "schedule_id",
        ),
    )

    user_schedule_id: int = Field(foreign_key="user_schedule.id")
    schedule_id: int = Field(foreign_key="schedule.id")

    absence_date: date = Field(index=True)
    note: str = Field(default="")

    updated_at: BrazilDatetime = Field(default_factory=BrazilDatetime.now_utc)
    created_at: BrazilDatetime = Field(default_factory=BrazilDatetime.now_utc)

    entry: "UserScheduleEntry" = Field(foreign_key="user_schedule_entry.id")
