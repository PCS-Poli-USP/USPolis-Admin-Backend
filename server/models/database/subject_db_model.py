from datetime import datetime

from beanie import Document, Link, Indexed
from fastapi import HTTPException, status
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
    async def by_id(cls, id: str) -> Self:
        subject = await Subject.get(id)
        if subject is None:
            raise SubjectNotFound(id)
        return subject

    @classmethod
    async def by_code(cls, code: str) -> Self:
        subject = await Subject.find_one(cls.code == code)
        if subject is None:
            raise SubjectNotFound(code)
        return subject

    @classmethod
    async def check_code_exists(cls, code: str) -> bool:
        return await cls.find_one(cls.code == code) is not None


class SubjectNotFound(HTTPException):
    def __init__(self, subject_info: str) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, f"Subject {subject_info} not found")
