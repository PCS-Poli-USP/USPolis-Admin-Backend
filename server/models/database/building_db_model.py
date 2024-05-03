from datetime import datetime
from typing import Annotated

from beanie import Document, Indexed, Link
from fastapi import HTTPException


class Building(Document):
    name: Annotated[str, Indexed(unique=True)]
    created_by: Link["User"]  # type: ignore  # noqa: F821
    updated_at: datetime

    class Settings:
        name = "buildings"


class BuildingNotFound(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(404, detail)
