from datetime import datetime

from pydantic import BaseModel, field_validator


class HolidayBase(BaseModel):
    category_id: int
    name: str

    @field_validator("name")
    def validate_year(cls, name: str) -> str:
        if len(name) == 0:
            raise ValueError("Holiday name must don't be empty")
        return name


class HolidayRegister(HolidayBase):
    date: datetime


class HolidayUpdate(HolidayBase):
    date: datetime


class HolidayManyRegister(HolidayBase):
    dates: list[datetime]
