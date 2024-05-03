from pydantic import BaseModel


class BuildingRegister(BaseModel):
    name: str
