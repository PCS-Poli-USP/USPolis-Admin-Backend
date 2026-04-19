from datetime import date
from typing import TYPE_CHECKING
from sqlalchemy import CheckConstraint, Index
from sqlmodel import Field, Relationship

from server.models.database.base_db_model import BaseModel

if TYPE_CHECKING:
    from server.models.database.user_schedule_entry_db_model import UserScheduleEntry

from server.utils.brazil_datetime import BrazilDatetime


class UserSchedule(BaseModel):
    __table_args__ = (
        CheckConstraint(
            "end_date >= start_date",
            name="user_schedule_check_end_date_after_start_date",
        ),
        Index(
            "user_schedule_user_id_start_date_end_date_idx",
            "user_id",
            "start_date",
            "end_date",
        ),
    )

    user_id: int = Field(foreign_key="user.id")
    start_date: date
    end_date: date
    updated_at: BrazilDatetime = Field(default_factory=BrazilDatetime.now_utc)
    created_at: BrazilDatetime = Field(default_factory=BrazilDatetime.now_utc)

    entries: list["UserScheduleEntry"] = Relationship(
        back_populates="user_schedule",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
