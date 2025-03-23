from sqlmodel import Field, SQLModel


class ClassCalendarLink(SQLModel, table=True):
    class_id: int | None = Field(
        default=None, foreign_key="class.id", primary_key=True, ondelete="CASCADE"
    )
    calendar_id: int | None = Field(
        default=None, foreign_key="calendar.id", primary_key=True, ondelete="CASCADE"
    )
