from datetime import datetime
from typing import Annotated

from beanie import Document, Indexed, Link
from pydantic import BaseModel


class BuildingRegister(BaseModel):
    name: str


class Building(Document, BuildingRegister):
    name: Annotated[str, Indexed(unique=True)]
    created_by: Link["User"]  # type: ignore  # noqa: F821
    updated_at: datetime

    class Settings:
        name = "buildings"
