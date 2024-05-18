from pydantic import BaseModel


class HolidayCategoryRegister(BaseModel):
    name: str


class HolidayCategoryUpdate(BaseModel):
    name: str