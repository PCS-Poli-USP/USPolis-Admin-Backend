from sqlmodel import Field, SQLModel


class ScheduleCalendarLink(SQLModel, table=True):
    schedule_id: int | None = Field(
        default=None, foreign_key="schedule.id", primary_key=True
    )
    calendar_id: int | None = Field(
        default=None, foreign_key="calendar.id", primary_key=True
    )
