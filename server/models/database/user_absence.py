from datetime import date, datetime
from typing import TYPE_CHECKING
from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, Relationship

from server.models.database.base_db_model import BaseModel

if TYPE_CHECKING:
    from server.models.database.user_schedule_entry_db_model import UserScheduleEntry

from server.utils.brazil_datetime import BrazilDatetime


class UserAbsence(BaseModel, table=True):
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

    user_schedule_id: int = Field(index=True)
    schedule_id: int = Field(index=True)

    absence_date: date = Field(index=True)
    note: str = Field(default="")

    updated_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    created_at: datetime = Field(default_factory=BrazilDatetime.now_utc)

    entry: "UserScheduleEntry" = Relationship(back_populates="absences")
