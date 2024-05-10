from pydantic import BaseModel


class HolidayCategoryRegister(BaseModel):
    category: str


class HolidayCategoryUpdate(BaseModel):
    category: str