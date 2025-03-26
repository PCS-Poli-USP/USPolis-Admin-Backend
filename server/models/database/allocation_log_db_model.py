from datetime import datetime
from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from server.models.database.schedule_db_model import Schedule
from server.utils.enums.action_type_enum import ActionType


class AllocationLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    modified_by: str = Field()
    modified_at: datetime = Field(default=datetime.now())
    action: ActionType = Field()

    old_classroom: str = Field()
    old_building: str = Field()
    new_classroom: str = Field()
    new_building: str = Field()

    schedule_id: int | None = Field(
        default=None, nullable=False, foreign_key="schedule.id"
    )
    schedule: "Schedule" = Relationship(back_populates="logs")
