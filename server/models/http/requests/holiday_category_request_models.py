from datetime import date
from pydantic import BaseModel


class HolidayCategoryRegister(BaseModel):
    name: str
    year: int = date.today().year


class HolidayCategoryUpdate(HolidayCategoryRegister):
    pass
