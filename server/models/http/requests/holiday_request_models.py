from pydantic import BaseModel
from datetime import datetime

class HolidayRegister(BaseModel):
    category_id: str
    date: datetime
    type: str

class HolidayUpdate(BaseModel):
    category_id: str
    date: datetime
    type: str

