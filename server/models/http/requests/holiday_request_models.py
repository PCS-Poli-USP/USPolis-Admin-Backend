from pydantic import BaseModel
from datetime import datetime

from server.utils.enums.holiday_type import HolidayType


class HolidayRegister(BaseModel):
    category_id: str
    date: datetime
    type: HolidayType


class HolidayUpdate(BaseModel):
    category_id: str
    date: datetime
    type: HolidayType
