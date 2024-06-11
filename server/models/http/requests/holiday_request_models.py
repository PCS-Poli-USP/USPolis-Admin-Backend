from datetime import datetime

from pydantic import BaseModel


class HolidayRegister(BaseModel):
    category_id: int
    date: datetime


class HolidayUpdate(BaseModel):
    category_id: int
    date: datetime


class HolidayManyRegister(BaseModel):
    category_id: int
    dates: list[datetime]
