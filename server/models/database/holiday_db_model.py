from datetime import date as datetime_date
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Relationship, SQLModel, Field


if TYPE_CHECKING:
    from server.models.database.user_db_model import User
    from server.models.database.holiday_category_db_model import HolidayCategory


class Holiday(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "date", "category_id", name="unique_holiday_date_for_category"
        ),
    )
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field()
    date: datetime_date = Field()
    updated_at: datetime = Field(default=datetime.now())

    category_id: int = Field(foreign_key="holidaycategory.id")
    category: "HolidayCategory" = Relationship(back_populates="holidays")

    created_by_id: int = Field(foreign_key="user.id")
    created_by: "User" = Relationship(back_populates="holidays")
