from datetime import datetime

from beanie import Document, Link, Indexed
from typing import Self, Annotated

from server.models.database.building_db_model import Building


class Subject(Document):
    buildings: list[Link[Building]] | None = None
    code: Annotated[str, Indexed(unique=True)]
    name: str
    professors: list[str]
    type: str
    class_credit: int
    work_credit: int
    activation: datetime
    desactivation: datetime | None = None

    class Settings:
        name = "subjects"  # Colletion Name
        keep_nulls = False

    @classmethod
    async def by_id(cls, id: str) -> Self | None:
        return await cls.get(id)

    @classmethod
    async def by_code(cls, code: str) -> Self | None:
        return await Subject.find_one(cls.code == code)
