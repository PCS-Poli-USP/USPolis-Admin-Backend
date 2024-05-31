from sqlmodel import Field, SQLModel


class CalendarHolidayCategoryLink(SQLModel, table=True):
    calendar_id: int | None = Field(
        default=None, foreign_key="calendar.id", primary_key=True
    )
    holiday_category_id: int | None = Field(
        default=None, foreign_key="holidaycategory.id", primary_key=True
    )
