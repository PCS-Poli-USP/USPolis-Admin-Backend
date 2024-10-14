from pydantic import BaseModel, field_validator

from server.models.validators.calendar.calendar_validator import CalendarValidator


class CalendarRegister(BaseModel):
    name: str
    categories_ids: list[int] | None = None

    @field_validator("name")
    def validate_year(cls, name: str) -> str:
        if not CalendarValidator.validate_name(name):
            raise ValueError("Calendar name must don't be empty")
        return name


class CalendarUpdate(CalendarRegister):
    categories_ids: list[int] | None = None
