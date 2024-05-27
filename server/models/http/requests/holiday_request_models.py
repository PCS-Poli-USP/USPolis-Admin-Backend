from pydantic import BaseModel
from datetime import datetime


class HolidayRegister(BaseModel):
    category_id: str
    date: datetime


class HolidayUpdate(BaseModel):
    category_id: str
    date: datetime
