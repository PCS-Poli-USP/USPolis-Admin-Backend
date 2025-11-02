from datetime import date
from fastapi import HTTPException, status
from pydantic import BaseModel, field_validator

from server.models.http.validators.calendar.calendar_validator import CalendarValidator


class CalendarRegister(BaseModel):
    name: str
    year: int = date.today().year
    categories_ids: list[int] | None = None

    @field_validator("name")
    def validate_year(cls, name: str) -> str:
        if not CalendarValidator.validate_name(name):
            raise CalendarInvalidInput("Nome do calendário não pode ser vazio")
        return name


class CalendarUpdate(CalendarRegister):
    pass


class CalendarInvalidInput(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
